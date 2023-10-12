// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package ccachemanagerpkg

import (
	"context"
	"errors"
	"fmt"
	"path/filepath"
	"io/ioutil"
	"os"
	"time"

	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/azureblobstorage"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/jsonutils"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/logger"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/shell"
)

const (
	CCacheTarSuffix = "-ccache.tar.gz"
	CCacheTagSuffix = "-latest-build.txt"
	// This are just place holders when constructing a new manager object.
	UninitializedGroupName = "unknown"
	UninitializedGroupSize = 0
	UninitializedGroupArchitecture = "unknown"
)

type RemoteStoreConfig struct {
	Type            string `json:"type"`
	TenantId        string `json:"tenantId"`
	UserName        string `json:"userName"`
	Password        string `json:"password"`
	StorageAccount  string `json:"storageAccount"`
	ContainerName   string `json:"containerName"`
	TagsFolder      string `json:"tagsFolder"`
	DownloadEnabled bool   `json:"downloadEnabled"`
	DownloadLatest  bool   `json:"downloadLatest"`
	DownloadFolder  string `json:"downloadFolder"`
	UploadEnabled   bool   `json:"uploadEnabled"`
	UploadFolder    string `json:"uploadFolder"`
	UpdateLatest    bool   `json:"updateLatest"`
	KeepLatestOnly  bool   `json:"keepLatestOnly"`
}

type CCacheGroupConfig struct {
	Name         string   `json:"name"`
	Comment      string   `json:"comment"`
	Enabled      bool     `json:"enabled"`
	PackageNames []string `json:"packageNames"`
}

type CCacheConfiguration struct {
	RemoteStoreConfig *RemoteStoreConfig  `json:"remoteStore"`
	Groups            []CCacheGroupConfig `json:"groups"`
}

type CCacheArchive struct {
	LocalSourcePath  string
	RemoteSourcePath string
	LocalTargetPath  string
	RemoteTargetPath string
}

type CCachePkgGroup struct {
	Name      string
	Enabled   bool
	Size      int
	Arch      string
	CCacheDir string

	TarFile   *CCacheArchive
	TagFile   *CCacheArchive
}

type CCacheManager struct {
	ConfigFileName    string
	Configuration     *CCacheConfiguration
	RootCCacheDir     string
	LocalDownloadsDir string
	LocalUploadsDir   string
	CurrentPkgGroup   *CCachePkgGroup
	AzureBlobStorage  *azureblobstoragepkg.AzureBlobStorage
}

func buildRemotePath(arch, folder, name, suffix string) (string) {
	return arch + "/" + folder + "/" + name + suffix
}

func (g *CCachePkgGroup) buildTarRemotePath(folder string) (string) {
	return buildRemotePath(g.Arch, folder, g.Name, CCacheTarSuffix)
}

func (g *CCachePkgGroup) buildTagRemotePath(folder string) (string) {
	return buildRemotePath(g.Arch, folder, g.Name, CCacheTagSuffix)
}

func (g *CCachePkgGroup) UpdateTagsPaths(remoteStoreConfig *RemoteStoreConfig, localDownloadsDir string, localUploadsDir string) {

	tagFile := &CCacheArchive{
		LocalSourcePath : localDownloadsDir + "/" + g.Name + CCacheTagSuffix,
		RemoteSourcePath : g.buildTagRemotePath(remoteStoreConfig.TagsFolder),
		LocalTargetPath : localUploadsDir + "/" + g.Name + CCacheTagSuffix,
		RemoteTargetPath : g.buildTagRemotePath(remoteStoreConfig.TagsFolder),
	}

	logger.Log.Infof("  tag local source  : (%s)", tagFile.LocalSourcePath)
	logger.Log.Infof("  tag remote source : (%s)", tagFile.RemoteSourcePath)
	logger.Log.Infof("  tag local target  : (%s)", tagFile.LocalTargetPath)
	logger.Log.Infof("  tag remote target : (%s)", tagFile.RemoteTargetPath)

	g.TagFile = tagFile
}

func (g *CCachePkgGroup) UpdateTarPaths(remoteStoreConfig *RemoteStoreConfig, localDownloadsDir string, localUploadsDir string) {

	tarFile := &CCacheArchive{
		LocalSourcePath : localDownloadsDir + "/" + g.Name + CCacheTarSuffix,
		RemoteSourcePath : g.buildTarRemotePath(remoteStoreConfig.DownloadFolder),
		LocalTargetPath : localUploadsDir + "/" + g.Name + CCacheTarSuffix,
		RemoteTargetPath : g.buildTarRemotePath(remoteStoreConfig.UploadFolder),
	}

	logger.Log.Infof("  tar local source  : (%s)", tarFile.LocalSourcePath)
	logger.Log.Infof("  tar remote source : (%s)", tarFile.RemoteSourcePath)
	logger.Log.Infof("  tar local target  : (%s)", tarFile.LocalTargetPath)
	logger.Log.Infof("  tar remote target : (%s)", tarFile.RemoteTargetPath)

	g.TarFile = tarFile
}

func (g *CCachePkgGroup) getLatestTag(azureBlobStorage *azureblobstoragepkg.AzureBlobStorage, containerName string) (string, error) {

	logger.Log.Infof("  checking if (%s) already exists...", g.TagFile.LocalSourcePath)
	_, err := os.Stat(g.TagFile.LocalSourcePath)
	if err != nil {
		// If file is not available locally, try downloading it...
		logger.Log.Infof("  downloading (%s) to (%s)...", g.TagFile.RemoteSourcePath, g.TagFile.LocalSourcePath)
		err = azureBlobStorage.Download(context.Background(), containerName, g.TagFile.RemoteSourcePath, g.TagFile.LocalSourcePath)
		if err != nil {
			logger.Log.Warnf("  unable to download ccache tag file.")
			return "", err
		}
	}

	latestBuildTagData, err := ioutil.ReadFile(g.TagFile.LocalSourcePath)
	if err != nil {
		logger.Log.Warnf("Unable to read ccache tag file contents. Error: %v", err)
		return "", err
	}

	return string(latestBuildTagData), nil
}

// SetCurrentPkgGroup() is called once per package.
func (m *CCacheManager) SetCurrentPkgGroup(basePackageName string, arch string) (err error) {
	// Note that findGroup() always succeeds.
	// If it cannot find the package, it assumes the packages belongs to the
	// 'common' group.
	groupName, groupEnabled, groupSize := m.findGroup(basePackageName)

	return m.setCurrentPkgGroupInternal(groupName, groupEnabled, groupSize, arch)
}

// setCurrentPkgGroupInternal() is called once per package.
func (m *CCacheManager) setCurrentPkgGroupInternal(groupName string, groupEnabled bool, groupSize int, arch string) (err error) {

	ccachePkgGroup := &CCachePkgGroup{
		Name   : groupName,
		Enabled: groupEnabled,
		Size   : groupSize,
		Arch   : arch,
	}

	ccachePkgGroup.CCacheDir, err = m.buildPkgCCacheDir(ccachePkgGroup.Name, ccachePkgGroup.Arch)
	if err != nil {
		return errors.New(fmt.Sprintf("Failed to construct the ccache directory name. Error (%v)", err))
	}

	// Note that we create the ccache working folder here as opposed to the
	// download function because there is a case where the group is configured
	// to enable ccache, but does not download.
	if ccachePkgGroup.Enabled {
		logger.Log.Infof("  ccache pkg folder : (%s)", ccachePkgGroup.CCacheDir)
		err = ensureDirExists(ccachePkgGroup.CCacheDir)
		if err != nil {
			logger.Log.Warnf("Cannot create ccache download folder.")
			return err
		}

		ccachePkgGroup.UpdateTagsPaths(m.Configuration.RemoteStoreConfig, m.LocalDownloadsDir, m.LocalUploadsDir)

		if m.Configuration.RemoteStoreConfig.DownloadLatest {

			logger.Log.Infof("  ccache is configured to use the latest from the remote store...")
			latestTag, err := ccachePkgGroup.getLatestTag(m.AzureBlobStorage, m.Configuration.RemoteStoreConfig.ContainerName)
			if err == nil {
				// Adjust the download folder from 'latest' to the tag loaded from the file...
				logger.Log.Infof("  updating (%s) to (%s)...", m.Configuration.RemoteStoreConfig.DownloadFolder, latestTag)
				m.Configuration.RemoteStoreConfig.DownloadFolder = latestTag
			} else {
				logger.Log.Warnf("  unable to get the latest ccache tag. Might be the first run and no ccache tag has been uploaded before.")
			}
		}

		if m.Configuration.RemoteStoreConfig.DownloadFolder == "" {
			logger.Log.Infof("  ccache archive source download folder is an empty string. Disabling ccache download.")
			m.Configuration.RemoteStoreConfig.DownloadEnabled = false
		}

		ccachePkgGroup.UpdateTarPaths(m.Configuration.RemoteStoreConfig, m.LocalDownloadsDir, m.LocalUploadsDir)
	}

	m.CurrentPkgGroup = ccachePkgGroup

	return nil
}

func loadConfiguration(configFileName string) (configuration *CCacheConfiguration, err error) {

	logger.Log.Infof("  loading ccache configuration file: %s", configFileName)

	err = jsonutils.ReadJSONFile(configFileName, &configuration)
	if err != nil {
		logger.Log.Infof("Failed to load file. %v", err)
		return nil, err
	}

	logger.Log.Infof("    Type           : %s", configuration.RemoteStoreConfig.Type)
	logger.Log.Infof("    TenantId       : %s", configuration.RemoteStoreConfig.TenantId)
	logger.Log.Infof("    UserName       : %s", configuration.RemoteStoreConfig.UserName)
	logger.Log.Infof("    StorageAccount : %s", configuration.RemoteStoreConfig.StorageAccount)
	logger.Log.Infof("    ContainerName  : %s", configuration.RemoteStoreConfig.ContainerName)
	logger.Log.Infof("    Tagsfolder     : %s", configuration.RemoteStoreConfig.TagsFolder)
	logger.Log.Infof("    DownloadEnabled: %v", configuration.RemoteStoreConfig.DownloadEnabled)
	logger.Log.Infof("    DownloadFolder : %s", configuration.RemoteStoreConfig.DownloadFolder)
	logger.Log.Infof("    UploadEnabled  : %v", configuration.RemoteStoreConfig.UploadEnabled)
	logger.Log.Infof("    UploadFolder   : %s", configuration.RemoteStoreConfig.UploadFolder)
	logger.Log.Infof("    UpdateLatest   : %v", configuration.RemoteStoreConfig.UpdateLatest)

	return configuration, err	
}

func ensureDirExists(dirName string) (err error) {
	_, err = os.Stat(dirName)
	if err == nil {
		return nil
	}

	if os.IsNotExist(err) {
		err = os.MkdirAll(dirName, 0755)
		if err != nil {
			logger.Log.Warnf("Unable to create folder (%s). Error: %v", dirName, err)
			return err
		}
	} else {
		logger.Log.Warnf("An error occured while checking if (%s) exists. Error: %v", dirName, err)
		return err
	}

	return nil
}


func compressDir(sourceDir string, archiveName string) (err error) {

	// Ensure the output file does not exist...
	_, err = os.Stat(archiveName)
	if err == nil {
		err = os.Remove(archiveName)
		if err != nil {
			logger.Log.Warnf("  unable to delete ccache out tar. Error: %v", err)
			return err
		}
	}

	// Create the archive...
	logger.Log.Infof("  compressing (%s) into (%s).", sourceDir, archiveName)
	compressStartTime := time.Now()
	tarArgs := []string{
		"cf",
		archiveName,
		"-C",
		sourceDir,
		"."}

	_, stderr, err := shell.Execute("tar", tarArgs...)
	if err != nil {
		logger.Log.Warnf("Unable compress ccache files itno archive. Error: %v", stderr)
		return err
	}
	compressEndTime := time.Now()
	logger.Log.Infof("  compress time: %s", compressEndTime.Sub(compressStartTime))	
	return nil
}

func uncompressFile(archiveName string, targetDir string) (err error) {
	logger.Log.Infof("  uncompressing (%s) into (%s).", archiveName, targetDir)
	uncompressStartTime := time.Now()
	tarArgs := []string{
		"xf",
		archiveName,
		"-C",
		targetDir,
		"."}

	_, stderr, err := shell.Execute("tar", tarArgs...)
	if err != nil {
		logger.Log.Warnf("Unable extract ccache files from archive. Error: %v", stderr)
		return err
	}
	uncompressEndTime := time.Now()
	logger.Log.Infof("  uncompress time: %v", uncompressEndTime.Sub(uncompressStartTime))
	return nil
}

func getChildFolders(parentFolder string) ([]string, error) {
	childFolders := []string{}

	dir, err := os.Open(parentFolder)
	if err != nil {
		logger.Log.Infof("  error opening parent folder. Error: (%v)", err)
		return nil, err
	}
	defer dir.Close()

	children, err := dir.Readdirnames(-1)
	if err != nil {
		logger.Log.Infof("  error enumerating children. Error: (%v)", err)
		return nil, err
	}

	for _, child := range children {
		childPath := filepath.Join(parentFolder, child)

		info, err := os.Stat(childPath)
		if err != nil {
			logger.Log.Infof("  error retrieving child attributes. Error: (%v)", err)
			continue
		}

		if info.IsDir() {
			childFolders = append(childFolders, child)
		}
	}

	return childFolders, nil
}

func CreateManager(rootDir string, configFileName string) (m *CCacheManager, err error) {

	logger.Log.Infof("* Creating a ccache manager instance *")
	logger.Log.Infof("  ccache root folder         : (%s)", rootDir)
	logger.Log.Infof("  ccache remote configuration: (%s)", configFileName)

	if rootDir == "" {
		return nil, errors.New("CCache root directory cannot be empty.")
	}

	if configFileName == "" {
		return nil, errors.New("CCache configuration file cannot be empty.")
	}

	configuration, err := loadConfiguration(configFileName)
	if err != nil {
		logger.Log.Infof("Failed to load remote store configuration. %v", err)
		return nil, err
	}

	logger.Log.Infof("  creating blob storage client...")
	accessType := azureblobstoragepkg.AnonymousAccess
	if configuration.RemoteStoreConfig.UploadEnabled {
		accessType = azureblobstoragepkg.AuthenticatedAccess
	}

	azureBlobStorage, err := azureblobstoragepkg.Create(configuration.RemoteStoreConfig.TenantId, configuration.RemoteStoreConfig.UserName, configuration.RemoteStoreConfig.Password, configuration.RemoteStoreConfig.StorageAccount, accessType)
	if err != nil {
		logger.Log.Warnf("Unable to init azure blob storage client.")
		return nil, err
	}

	err = ensureDirExists(rootDir)
	if err != nil {
		logger.Log.Warnf("  cannot create ccache working folder.")
		return nil, err
	}

	localDownloadsDir := rootDir + "-downloads"
	err = ensureDirExists(localDownloadsDir)
	if err != nil {
		logger.Log.Warnf("  cannot create ccache downloads folder.")
		return nil, err
	}

	localUploadsDir := rootDir + "-uploads"
	err = ensureDirExists(localUploadsDir)
	if err != nil {
		logger.Log.Warnf("  cannot create ccache uploads folder.")
		return nil, err
	}

	ccacheManager := &CCacheManager{
		ConfigFileName    : configFileName,
		Configuration     : configuration,
		RootCCacheDir     : rootDir,
		LocalDownloadsDir : localDownloadsDir,
		LocalUploadsDir   : localUploadsDir,
		AzureBlobStorage  : azureBlobStorage,
	}

	ccacheManager.setCurrentPkgGroupInternal(UninitializedGroupName, false, UninitializedGroupSize, UninitializedGroupArchitecture)

	return ccacheManager, nil
}

// This function returns groupName="common" and groupSize=0 if any failure is
// encountered. This allows the ccachemanager to 'hide' the details of packages
// that are not part of any remote storage group.
func (m *CCacheManager) findGroup(basePackageName string) (groupName string, groupEnabled bool, groupSize int) {
	//
	// We assume that:
	// - all packages want ccache enabled for them.
	// - each package belongs to its own group.
	// Then, we iterate to see if those assumptions do not apply for a certain
	// package and overwrite them with the actual configuration.
	//
	groupName = basePackageName
	groupEnabled = true
	groupSize = 1
	found := false

	for _, group := range m.Configuration.Groups {
		for _, packageName := range group.PackageNames {
			if packageName == basePackageName {
				logger.Log.Infof("  found group (%s) for base package (%s)...", group.Name, basePackageName)
				groupName = group.Name
				groupEnabled = group.Enabled
				groupSize = len(group.PackageNames)
				if !groupEnabled {
					logger.Log.Infof("  ccache is explicitly disabled for this group in the ccache configuration.")
				}
				found = true
				break
			}
		}
		if found {
			break
		}
	}

	return groupName, groupEnabled, groupSize
}

func (m *CCacheManager) findCCacheGroupInfo(groupName string) (groupEnabled bool, groupSize int) {
	//
	// We assume that:
	// - all packages want ccache enabled for them.
	// - each package belongs to its own group.
	// Then, we iterate to see if those assumptions do not apply for a certain
	// package and overwrite them with the actual configuration.
	//
	groupEnabled = true
	groupSize = 1

	for _, group := range m.Configuration.Groups {
		if groupName == group.Name {
			groupEnabled = group.Enabled
			groupSize = len(group.PackageNames)
		}
	}

	return groupEnabled, groupSize
}

func (m *CCacheManager) buildPkgCCacheDir(pkgCCacheGroupName string, pkgArchitecture string) (string, error) {
	if pkgArchitecture == "" {
		return "", errors.New("CCache package pkgArchitecture cannot be empty.")
	}
	if pkgCCacheGroupName == "" {
		return "", errors.New("CCache package group name cannot be empty.")
	}
	return m.RootCCacheDir + "/" + pkgArchitecture + "/" + pkgCCacheGroupName, nil
}

func (m *CCacheManager) DownloadPkgGroupCCache() (err error) {

	logger.Log.Infof("* processing download of ccache artifacts...")

	remoteStoreConfig := m.Configuration.RemoteStoreConfig
	if !remoteStoreConfig.DownloadEnabled {
		logger.Log.Infof("  downloading archived ccache artifacts is disabled. Skipping download...")
		return nil
	}

	logger.Log.Infof("  downloading (%s) to (%s)...", m.CurrentPkgGroup.TarFile.RemoteSourcePath, m.CurrentPkgGroup.TarFile.LocalSourcePath)
	err = m.AzureBlobStorage.Download(context.Background(), remoteStoreConfig.ContainerName, m.CurrentPkgGroup.TarFile.RemoteSourcePath, m.CurrentPkgGroup.TarFile.LocalSourcePath)
	if err != nil {
		logger.Log.Warnf("  unable to download ccache archive.")
		return err
	}

	err = uncompressFile(m.CurrentPkgGroup.TarFile.LocalSourcePath, m.CurrentPkgGroup.CCacheDir)
	if err != nil {
		logger.Log.Warnf("Unable uncompress ccache files from archive.")
		return err
	}

	return nil
}

func (m *CCacheManager) UploadPkgGroupCCache() (err error) {

	logger.Log.Infof("* processing upload of ccache artifacts...")

	// Check if ccache has actually generated any content.
	// If it has, it would have created a specific folder structure - so,
	// checking for folders is reasonable enough.
	pkgCCacheDirContents, err := getChildFolders(m.CurrentPkgGroup.CCacheDir)
	if err != nil {
		logger.Log.Warnf("Failed to enumerate the contents of (%s).", m.CurrentPkgGroup.CCacheDir)
	}
	if len(pkgCCacheDirContents) == 0 {
		logger.Log.Infof("  %s is empty. Nothing to archive and upload. Skipping...", m.CurrentPkgGroup.CCacheDir)
		return nil
	}

    remoteStoreConfig := m.Configuration.RemoteStoreConfig
	if !remoteStoreConfig.UploadEnabled {
		logger.Log.Infof("  ccache update is disabled for this build.")
		return nil
	}

	err = compressDir(m.CurrentPkgGroup.CCacheDir, m.CurrentPkgGroup.TarFile.LocalTargetPath)
	if err != nil {
		logger.Log.Warnf("Unable compress ccache files itno archive.")
		return err
	}

	// Upload the ccache archive
	logger.Log.Infof("  uploading ccache archive (%s) to (%s)...", m.CurrentPkgGroup.TarFile.LocalTargetPath, m.CurrentPkgGroup.TarFile.RemoteTargetPath)
	err = m.AzureBlobStorage.Upload(context.Background(), m.CurrentPkgGroup.TarFile.LocalTargetPath, remoteStoreConfig.ContainerName, m.CurrentPkgGroup.TarFile.RemoteTargetPath)
	if err != nil {
		logger.Log.Warnf("Unable to upload ccache archive.")
		return err
	}

	if remoteStoreConfig.UpdateLatest {
		logger.Log.Infof("  update latest is enabled.")
		// If KeepLatestOnly is true, we need to capture the current source
		// ccache archive path which is about to be dereferenced. That way,
		// we can delete it after we update the latest tag to point to the
		// new ccache archive.
		//
		// First we assume it does not exist (i.e. first time to run).
		//
		previousLatestTarSourcePath := ""
		if remoteStoreConfig.KeepLatestOnly {
			logger.Log.Infof("  keep latest only is enabled. Capturing path to previous ccache archive if it exists...")
			// getLatestTag() will check locally first if the tag file has
			// been downloaded and use it. If not, it will attempt to
			// download it. If not, then there is no way to get to the
			// previous latest tar (if it exists at all).
			latestTag, err := m.CurrentPkgGroup.getLatestTag(m.AzureBlobStorage, m.Configuration.RemoteStoreConfig.ContainerName)
			if err == nil {
				// build the archive remote path based on the latestTag.
				previousLatestTarSourcePath = m.CurrentPkgGroup.buildTarRemotePath(latestTag)
				logger.Log.Infof("  (%s) is about to be de-referenced.", previousLatestTarSourcePath)
			} else {
				logger.Log.Warnf("  unable to get the latest ccache tag. This might be the first run and no latest ccache tag has been uploaded before.")
			}
		}

		// Create the latest tag file...
		logger.Log.Infof("  creating a tag file (%s) with content: (%s)...", m.CurrentPkgGroup.TagFile.LocalTargetPath, remoteStoreConfig.UploadFolder)
		err = ioutil.WriteFile(m.CurrentPkgGroup.TagFile.LocalTargetPath, []byte(remoteStoreConfig.UploadFolder), 0644)
		if err != nil {
			logger.Log.Warnf("Unable to write tag information to temporary file. Error: %v", err)
			return err
		}

		// Upload the latest tag file...
		logger.Log.Infof("  uploading tag file (%s) to (%s)...", m.CurrentPkgGroup.TagFile.LocalTargetPath, m.CurrentPkgGroup.TagFile.RemoteTargetPath)
		err = m.AzureBlobStorage.Upload(context.Background(), m.CurrentPkgGroup.TagFile.LocalTargetPath, remoteStoreConfig.ContainerName, m.CurrentPkgGroup.TagFile.RemoteTargetPath)
		if err != nil {
			logger.Log.Warnf("Unable to upload ccache archive.")
			return err
		}

		if remoteStoreConfig.KeepLatestOnly {
			logger.Log.Infof("  keep latest only is enabled. Removing previous ccache archive if it exists...")
			if previousLatestTarSourcePath == "" {
				logger.Log.Infof("  cannot remove old archive with an empty name. No previous ccache archive to remove.")
			} else {
				logger.Log.Infof("  removing ccache archive (%s) from remote store...", previousLatestTarSourcePath)
				err = m.AzureBlobStorage.Delete(context.Background(), remoteStoreConfig.ContainerName, previousLatestTarSourcePath)
				if err != nil {
					logger.Log.Warnf("Unable to remove previous ccache archive.")
				}
			}
		}
	}

	return nil
}

//
// After building a package or more, the ccache folder is expected to look as
// follows:
//
// <m.RootCCacheDir>
//   x86_64
//     <groupName-1>
//     <groupName-2>
//   noarch
//     <groupName-3>
//     <groupName-4>
//
// This function is typically called at the end of the build - after all
// packages have completed building.
//
// At that point, there is not per package information about the group name
// or the architecture.
//
// We use this directory structure to encode the per package group information
// at build time, so we can use them now.
//
func (m *CCacheManager) UploadMultiPkgGroupCCaches() (err error) {

	architectures, err := getChildFolders(m.RootCCacheDir)
	errorsOccured := false
	if err != nil {
		return errors.New(fmt.Sprintf("failed to enumerate ccache child folders under (%s)...", m.RootCCacheDir))
	} 

	for _, architecture := range architectures {
		groupNames, err := getChildFolders(filepath.Join(m.RootCCacheDir, architecture))
		if err != nil {
			logger.Log.Warnf("failed to enumerate child folders under (%s)...", m.RootCCacheDir)
			errorsOccured = true
		} else {
			for _, groupName := range groupNames {
				// Enable this continue only if we enable uploading as
				// soon as packages are done building.
				groupEnabled, groupSize := m.findCCacheGroupInfo(groupName)

				if !groupEnabled {
					// This should never happen unless a previous run had it
					// enabled and the folder got created. The correct behavior
					// is that the folder is not even created before the pkg
					// build starts and hence by reaching this method, it
					// should not be there.
					//
					logger.Log.Infof("  ccache is explicitly disabled for this group in the ccache configuration. Skipping...")
					continue
				}

				if groupSize < 2 {
					// This has either been processed earlier or there is
					// nothing to process.
					continue
				}

				groupCCacheDir, err := m.buildPkgCCacheDir(groupName, architecture)
				if err != nil {
					logger.Log.Warnf("Failed to get ccache dir for architecture (%s) and group name (%s)...", architecture, groupName)
					errorsOccured = true
				}				
				logger.Log.Infof("  processing ccache folder (%s)...", groupCCacheDir)

				m.setCurrentPkgGroupInternal(groupName, groupEnabled, groupSize, architecture)

				err = m.UploadPkgGroupCCache()
				if err != nil {
					errorsOccured = true
					logger.Log.Warnf("CCache will not be archived for (%s) (%s)...", architecture, groupName)
				}
			}
		}
	}

	if errorsOccured {
		return errors.New("CCache archiving and upload failed. See above warning for more details.")
	}
	return nil
}