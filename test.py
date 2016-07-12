import FileSystem;
import codecs, os, sys;
sys.stdout = codecs.getwriter("cp437")(sys.stdout, "replace");

sTempFolderPath = FileSystem.fsFullPath(os.environ["TEMP"]);
sSpecialChars = 'test[[["<>\\/?*:|]]]';

sSpecialCharsPath = FileSystem.fsFullPath(sTempFolderPath, sSpecialChars);

print "* Testing file operations with special characters..."; 
sTranslatedSpecialChars = FileSystem.fsTranslateToValidName(sSpecialChars);
sData = "x";

# Clean old files/folders
print "* Cleaning up old files/folders..."; 
print "  * Checking if old test file exists..."; 
ebIsFileResult = FileSystem.febIsFile(sTempFolderPath, sTranslatedSpecialChars);
assert isinstance(ebIsFileResult, bool), "Expected febIsFile result to be a boolean, got %s" % repr(ebIsFileResult);
if ebIsFileResult:
  print "  * Deleting old test file..."; 
  ebDeleteFileResult = FileSystem.febDeleteFile(sTempFolderPath, sTranslatedSpecialChars);
  assert ebDeleteFileResult is True, "Expected febDeleteFile result to be True, got %s" % repr(ebDeleteFileResult);
print "  * Checking if old test folder exists..."; 
ebIsFolderResult = FileSystem.febIsFolder(sTempFolderPath, sTranslatedSpecialChars);
assert isinstance(ebIsFolderResult, bool), "Expected febIsFolder result to be a boolean, got %s" % repr(ebIsFolderResult);
if ebIsFolderResult:
  print "  * Deleting old test folder..."; 
  ebDeleteFolderResult = FileSystem.febDeleteFolder(sTempFolderPath, sTranslatedSpecialChars);
  assert ebDeleteFolderResult is True, "Expected febDeleteFolder result to be True, got %s" % repr(ebDeleteFolderResult);

print "* Creating file with special characters..."; 
# Create a file, detect it, read it and delete it.
eWriteFileResult = FileSystem.feWriteDataToFile(sData, sTempFolderPath, sTranslatedSpecialChars);
assert eWriteFileResult is None, "Expected feWriteDataToFile result to be None, got %s" % repr(eWriteFileResult);
print "  * Checking if file with special characters exists..."; 
ebIsFileResult = FileSystem.febIsFile(sTempFolderPath, sTranslatedSpecialChars);
assert ebIsFileResult is True, "Expected febIsFile result to be True, got %s" % repr(ebIsFileResult);
print "  * Reading file with special characters..."; 
esReadFileResult = FileSystem.fesReadDataFromFile(sTempFolderPath, sTranslatedSpecialChars);
assert esReadFileResult == sData, "Expected febReadDataFromFile result to be %s, got %s" % (repr(sData), repr(esReadFileResult));
print "  * Deletiong file with special characters..."; 
ebDeleteFileResult = FileSystem.febDeleteFile(sTempFolderPath, sTranslatedSpecialChars);
assert ebDeleteFileResult is True, "Expected febDeleteFile result to be True, got %s" % repr(ebDeleteFileResult);

print "* Testing folder operations with special characters...";
# Create a folder, detect it, create a file in the folder and delete the folder.
print "  * Creating folder with special characters..."; 
ebCreateFolderResult = FileSystem.febCreateFolder("x", sTempFolderPath, sTranslatedSpecialChars);
assert ebCreateFolderResult is True, "Expected febCreateFolder result to be True, got %s" % repr(ebCreateFolderResult);
print "  * Checking if folder with special characters exists..."; 
ebIsFolderResult = FileSystem.febIsFolder(sTempFolderPath, sTranslatedSpecialChars);
assert ebIsFolderResult is True, "Expected febIsFolder result to be True, got %s" % repr(ebIsFolderResult);
print "  * Creating file with special characters in folder with special characters..."; 
eWriteFileResult = FileSystem.feWriteDataToFile(sData, sTempFolderPath, sTranslatedSpecialChars, sTranslatedSpecialChars);
assert eWriteFileResult is None, "Expected feWriteDataToFile result to be None, got %s" % repr(eWriteFileResult);
print "  * Deletiong folder with special characters containing a file with special characters..."; 
ebDeleteFolderResult = FileSystem.febDeleteFolder(sTempFolderPath, sTranslatedSpecialChars);
assert ebDeleteFolderResult is True, "Expected febDeleteFolder result to be True, got %s" % repr(ebDeleteFolderResult);

print "+ All tests passed."