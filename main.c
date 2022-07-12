#include <dirent.h>
#include <endian.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

  // ensure we're at least given the essentials
  if (argc < 2) {
    fprintf(stderr, "please supply filename\n");
    return 1;
  }

  // grab and ensure we see the file
  FILE *inputFile;
  char *inputFileName = argv[1];
  inputFile = fopen(inputFileName, "rb");
  if (inputFile == NULL) {
    fprintf(stderr, "cannot open input file: %s\n", inputFileName);
    return 1;
  } else {
    fprintf(stdout, "successfully loaded file: %s\n\n", inputFileName);
  }

  int numFiles = 0;
  for (int i = 0; i < 512; i++) {
    int offset;
    int size;
    uint32_t inputBuffer;
    fread(&inputBuffer, sizeof(inputBuffer), 1, inputFile);
    if (i % 2 == 0) {
      // if what we just read was an offset
      offset = htole32(inputBuffer);
    } else {
      // if what we just read was a size
      size = htole32(inputBuffer);
      if (offset * 2 != 0 && size != 0) {
        // if we have a non-zero offset and a size, we found a file.
        numFiles++;

        char *outputFileName[32];
        char *buffer[sizeof(inputBuffer)];
        sprintf(*outputFileName, "file_%i", numFiles);
        FILE *seekFile = fopen(inputFileName, "rb");
        FILE *outputFile = fopen(*outputFileName, "wb");

        fseek(seekFile, offset, SEEK_SET);
        for (int j = 0; j < size; j += sizeof(buffer)) {
          fread(buffer, sizeof(buffer), 1, seekFile);
          fwrite(buffer, sizeof(buffer), 1, outputFile);
        }

        int offset = 0;
        int size = 0;
        fclose(seekFile);
        fclose(outputFile);
      }
    }
  }

  fprintf(stdout, "Found %i files.", numFiles);
  fclose(inputFile);
  return 0;
}