import FileSystem;
import os;

sTempFolderPath = FileSystem.fsFullPath(os.environ["TEMP"]);
sSpecialChars = '"<>\\/?*:|';

sSpecialCharsPath = FileSystem.fsFullPath(sTempFolderPath, sSpecialChars);

print "Testing special characters..."; 
sTranslatedSpecialChars = FileSystem.fsTranslateToValidName(sSpecialChars);
# As a file
FileSystem.fbWriteDataToFile("x", sTempFolderPath, sTranslatedSpecialChars);
assert FileSystem.fbIsFile(sTempFolderPath, sTranslatedSpecialChars);
FileSystem.fbDeleteFile(sTempFolderPath, sTranslatedSpecialChars);
# As a folder
FileSystem.fbCreateFolder("x", sTempFolderPath, sTranslatedSpecialChars);
assert FileSystem.fbIsFolder(sTempFolderPath, sTranslatedSpecialChars);
FileSystem.fbDeleteFolder(sTempFolderPath, sTranslatedSpecialChars);
