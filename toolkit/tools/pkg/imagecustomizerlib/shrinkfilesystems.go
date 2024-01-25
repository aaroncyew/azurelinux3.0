package imagecustomizerlib

import (
	"fmt"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/imagegen/diskutils"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/logger"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/shell"
	"math"
	"regexp"
	"strconv"
	"strings"
)

func shrinkFilesystems(imageLoopDevice string, outputImageFile string) error {
	logger.Log.Infof("Shrinking filesystems")

	// Get partition info
	diskPartitions, err := diskutils.GetDiskPartitions(imageLoopDevice)
	if err != nil {
		return err
	}

	// Get the start sectors of all partitions
	matchStarts, err := getStartSectors(imageLoopDevice, len(diskPartitions)-1)
	if err != nil {
		return err
	}

	for partitionNum := 0; partitionNum < len(diskPartitions); partitionNum++ {
		if diskPartitions[partitionNum].Type != "part" {
			continue
		}

		fstype := diskPartitions[partitionNum].FileSystemType
		// Currently only support ext2, ext3, ext4 filesystem types
		if fstype != "ext2" && fstype != "ext3" && fstype != "ext4" {
			continue
		}

		partitionLoopDevice := diskPartitions[partitionNum].Path

		// Check the file system with e2fsck
		err := shell.ExecuteLive(true /*squashErrors*/, "sudo", "e2fsck", "-fy", partitionLoopDevice)
		if err != nil {
			return fmt.Errorf("failed to check %s with e2fsck:\n%w", partitionLoopDevice, err)
		}

		// Shrink the file system with resize2fs -M
		stdout, stderr, err := shell.Execute("sudo", "resize2fs", "-M", partitionLoopDevice)
		if err != nil {
			return fmt.Errorf("failed to resize %s with resize2fs:\n%v", partitionLoopDevice, stderr)
		}

		// Find the new partition end value
		end, err := getNewPartitionEndInSectors(stdout, matchStarts[partitionNum-1][1], imageLoopDevice)
		if err != nil {
			return fmt.Errorf("failed to calculate new partition end: \n%w", err)
		}

		// Resize the partition with parted resizepart
		_, stderr, err = shell.ExecuteWithStdin("yes" /*stdin*/, "sudo", "parted", "---pretend-input-tty", imageLoopDevice, "resizepart", strconv.Itoa(partitionNum), end)
		if err != nil {
			return fmt.Errorf("failed to resizepart %s with parted:\n%v", partitionLoopDevice, stderr)
		}

		// Re-read the partition table
		err = shell.ExecuteLive(true, "flock", "--timeout", "5", imageLoopDevice, "partprobe", "-s", imageLoopDevice)
		if err != nil {
			return fmt.Errorf("partprobe failed: \n%w, err")
		}
	}
	return nil
}

// Get the start sectors of all partitions.
func getStartSectors(imageLoopDevice string, partitionCount int) (matchStarts [][]string, err error) {
	stdout, stderr, err := shell.Execute("sudo", "fdisk", "-l", imageLoopDevice)
	if err != nil {
		return nil, fmt.Errorf("fdisk failed to list partitions: \n%v", stderr)
	}

	// Since regexp.QuoteMeta doesn't escape forward slashes, handling it here
	escapeForwardSlashesLoopDevice := strings.ReplaceAll(imageLoopDevice, "/", `\/`)

	// Example line from fdisk -l output: "/dev/loop41p2   18432  103064   84633 41.3M Linux filesystem"
	reStarts := regexp.MustCompile(`(?m:^` + escapeForwardSlashesLoopDevice + `p\d+ *(\d+).*?)`)
	matchStarts = reStarts.FindAllStringSubmatch(stdout, -1)
	if len(matchStarts) < partitionCount {
		return nil, fmt.Errorf("could not find all partition starts")
	}

	return matchStarts, nil
}

// Get the filesystem size in sectors.
func getFilesystemSizeInSectors(resize2fsOutput string, imageLoopDevice string) (filesystemSizeInSectors int, err error) {
	// Example resize2fs output first line: "Resizing the filesystem on /dev/loop44p2 to 21015 (4k) blocks."
	re := regexp.MustCompile(`.*to (\d+) \((\d+)([a-zA-Z])\)`)
	// Get the block count and block size
	match := re.FindStringSubmatch(resize2fsOutput)
	if len(match) < 4 {
		return 0, fmt.Errorf("failed to parse output of resize2fs")
	}

	blockCount, err := strconv.Atoi(match[1]) // Example: 21015
	if err != nil {
		return 0, fmt.Errorf("failed to get block count: \n%w", err)
	}
	multiplier, err := strconv.Atoi(match[2]) // Example: 4
	if err != nil {
		return 0, fmt.Errorf("failed to get multiplier for block size: \n%w", err)
	}
	unit := match[3] // Example: 'k'

	// Calculate block size
	var blockSize int
	const KB = 1024 // kilobyte in bytes
	switch unit {
	case "k":
		blockSize = multiplier * KB
	default:
		return 0, fmt.Errorf("unrecognized unit %s", unit)
	}

	filesystemSizeInBytes := blockCount * blockSize

	// Get the sector size
	logicalSectorSize, _, err := diskutils.GetSectorSize(imageLoopDevice)
	if err != nil {
		fmt.Errorf("failed to get sector size")
	}
	sectorSizeInBytes := int(logicalSectorSize) // cast from uint64 to int

	return int(math.Ceil(float64(filesystemSizeInBytes) / float64(sectorSizeInBytes))), nil
}

// Get the new partition end in sectors.
func getNewPartitionEndInSectors(resize2fsOutput string, startSector string, imageLoopDevice string) (endInSectors string, err error) {
	filesystemSizeInSectors, err := getFilesystemSizeInSectors(resize2fsOutput, imageLoopDevice)
	if err != nil {
		return "", fmt.Errorf("failed to get filesystem size: \n%w", err)
	}

	// Convert start sector string to int
	start, err := strconv.Atoi(startSector)
	if err != nil {
		return "", fmt.Errorf("failed to convert start sector to int: \n%w", err)
	}
	// Calculate the new end
	end := start + filesystemSizeInSectors
	// Convert to a string with sectors unit appended
	endInSectors = strconv.Itoa(end) + "s"
	return endInSectors, nil
}
