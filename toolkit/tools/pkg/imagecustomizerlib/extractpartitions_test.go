package imagecustomizerlib

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"os"
	"testing"

	"github.com/microsoft/azurelinux/toolkit/tools/internal/file"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/logger"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/shell"
	"github.com/stretchr/testify/assert"
)

func TestAddSkippableFrame(t *testing.T) {
	// Create a skippable frame containing the metadata and prepend the frame to the partition file
	skippableFrameMetadata, err := createSkippableFrameMetadata()
	assert.NoError(t, err)

	// Create test raw partition file
	partitionRawFilepath, err := createTestRawPartitionFile("test.raw")
	assert.NoError(t, err)

	// Compress to .raw.zst partition file
	partitionFilepath, err := compressWithZstd(partitionRawFilepath)
	assert.NoError(t, err)

	// Test adding the skippable frame
	err = addSkippableFrame(partitionFilepath, SkippableFrameMagicNumber, SkippableFrameSize, skippableFrameMetadata)
	assert.NoError(t, err)

	// Verify decompression with skippable frame
	err = verifySkippableFrameDecompression(partitionRawFilepath, partitionFilepath)
	assert.NoError(t, err)

	// Verify skippable frame metadata
	err = verifySkippableFrameMetadataFromFile(partitionFilepath, SkippableFrameMagicNumber, SkippableFrameSize, skippableFrameMetadata)
	assert.NoError(t, err)

	// Remove test partition files
	err = os.Remove(partitionRawFilepath)
	assert.NoError(t, err)

	err = os.Remove(partitionFilepath)
	assert.NoError(t, err)
}

func createTestRawPartitionFile(filename string) (string, error) {
	// Test data
	data := []byte{0x01, 0x02, 0x03, 0x04, 0x05}

	err := writeToFile(filename, data)
	if err != nil {
		return "", err
	} else {
		logger.Log.Infof("File %s created successfully with dummy data.", filename)
		return filename, nil
	}
}

func writeToFile(fileName string, data []byte) error {
	file, err := os.Create(fileName)
	if err != nil {
		return err
	}
	defer file.Close()

	_, err = file.Write(data)
	if err != nil {
		return err
	}

	return nil
}

// Decompress the .raw.zst partition file and verifies the hash matches with the source .raw file
func verifySkippableFrameDecompression(rawPartitionFilepath string, rawZstPartitionFilepath string) (err error) {
	// Decompressing .raw.zst file
	decompressedPartitionFilepath := "decompressed.raw"
	err = shell.ExecuteLive(true, "zstd", "-d", rawZstPartitionFilepath, "-o", decompressedPartitionFilepath)
	if err != nil {
		return fmt.Errorf("failed to decompress %s with zstd:\n%w", rawZstPartitionFilepath, err)
	}

	// Calculating hashes
	rawPartitionFileHash, err := file.GenerateSHA256(rawPartitionFilepath)
	if err != nil {
		return fmt.Errorf("error: %w", err)
	}
	decompressedPartitionFileHash, err := file.GenerateSHA256(decompressedPartitionFilepath)
	if err != nil {
		return fmt.Errorf("error: %w", err)
	}

	// Verifying hashes are equal
	if rawPartitionFileHash != decompressedPartitionFileHash {
		return fmt.Errorf("decompressed partition file hash does not match source partition file hash: %s != %s", decompressedPartitionFileHash, rawPartitionFilepath)
	}
	logger.Log.Debugf("Decompressed partition file hash matches source partition file hash!")

	// Removing decompressed file
	err = os.Remove(decompressedPartitionFilepath)
	if err != nil {
		return fmt.Errorf("failed to remove raw file %s:\n%w", decompressedPartitionFilepath, err)
	}

	return nil
}

// Verifies that the skippable frame has been correctly prepended to the partition file with the correct data
func verifySkippableFrameMetadataFromFile(partitionFilepath string, magicNumber uint32, frameSize uint32, skippableFrameMetadata [SkippableFrameSize]byte) (err error) {
	// Read existing data from the partition file.
	existingData, err := os.ReadFile(partitionFilepath)
	if err != nil {
		return fmt.Errorf("failed to read partition file %s:\n%w", partitionFilepath, err)
	}

	// verify that the skippable frame has been prepended to the partition file by validating magicNumber
	var magicNumberByteArray [4]byte
	binary.LittleEndian.PutUint32(magicNumberByteArray[:], magicNumber)
	if !bytes.Equal(existingData[0:4], magicNumberByteArray[:]) {
		return fmt.Errorf("skippable frame has not been prepended to the partition file:\n %d != %d", existingData[0:4], magicNumberByteArray[:])
	}
	logger.Log.Infof("Skippable frame had been correctly prepended to the partition file...")

	// verify that the skippable frame has the correct frame size by validating frameSize
	var frameSizeByteArray [4]byte
	binary.LittleEndian.PutUint32(frameSizeByteArray[:], frameSize)
	if !bytes.Equal(existingData[4:8], frameSizeByteArray[:]) {
		return fmt.Errorf("skippable frame frameSize field does not match the defined frameSize:\n %d != %d", existingData[4:8], frameSizeByteArray[:])
	}
	logger.Log.Infof("Skippable frame frameSize field is correct...")

	// verify that the skippable frame has the correct inserted metadata by validating skippableFrameMetadata
	if !bytes.Equal(existingData[8:8+frameSize], skippableFrameMetadata[:]) {
		return fmt.Errorf("skippable frame metadata does not match the inserted metadata:\n %d != %d", existingData[8:8+frameSize], skippableFrameMetadata[:])
	}
	logger.Log.Infof("Skippable frame is valid and contains the correct metadata!")

	return nil
}
