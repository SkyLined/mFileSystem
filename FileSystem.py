import os, shutil, time;
# To solve any unicode errors you may get, add this line (without the "#") to your main python script:
# import codecs,sys; sys.stdout = codecs.getwriter("cp437")(sys.stdout, "replace");

# Try again almost immediately, then wait longer and longer
auPauses = [
  1, 4, 5, 10, 10, 30,  # one minute
  30, 30,               # two minutes
#  60, 60, 60,           # five minutes
#  300,                  # ten minutes
#  600,                  # tenty minutes
#  600,                  # thirty minutes
#  1800,                 # one hour
];                      # give up.

dsInvalidPathCharacterAsciiTranslationMap = {
  # Translates characters that are not valid in file/folder names to a visually similar unicode character.
  u'"':   u"''",     # Double APOSTROPHY
  u"<":   u"[",      # LEFT SQUARE BRACKET
  u">":   u"]",      # RIGHT SQUARE BRACKET
  u"\\":  u" ",      # SPACE
  u"/":   u" ",      # SPACE
  u"?":   u"!",      # EXCLAMATION MARK
  u"*":   u"x",      # LATIN SMALL LETTER X
  u":":   u".",      # FULL STOP
  u"|":   u"!",      # EXCLAMATION MARK
};
dsInvalidPathCharacterUnicodeTranslationMap = {
  # Translates characters that are not valid in file/folder names to a visually similar unicode character.
  u'"':   u"\u2033", # DOUBLE PRIME
  u"<":   u"\u3008", # LEFT ANGLE BRACKET
  u">":   u"\u3009", # RIGHT ANGLE BRACKET
  u"\\":  u"\u29F9", # BIG REVERSE SOLIDUS
  u"/":   u"\u29F8", # BIG SOLIDUS
  u"?":   u"\u061F", # ARABIC QUESTION MARK
  u"*":   u"\u204E", # LOWER ASTERISK
  u":":   u"\u0589", # ARMENIAN FULL STOP
  u"|":   u"\u01C0", # LATIN LETTER DENTAL CLICK
};
for uCharCode in xrange(0, 0x20):
  # Translate control codes
  dsInvalidPathCharacterAsciiTranslationMap[unichr(uCharCode)] = u"."; # FULL STOP
  dsInvalidPathCharacterUnicodeTranslationMap[unichr(uCharCode)] = u"\uFFFD"; # REPLACEMENT CHARACTER

def fsValidName(sName, bUnicode = True):
  dsInvalidPathCharacterTranslationMap = bUnicode \
      and dsInvalidPathCharacterUnicodeTranslationMap \
      or dsInvalidPathCharacterAsciiTranslationMap;
  return u"".join([
    (bUnicode or ord(sChar) < 0x100) and dsInvalidPathCharacterTranslationMap.get(sChar, sChar) or "."
    for sChar in unicode(sName)
  ]);

# http://msdn.microsoft.com/en-us/library/aa365247.aspx
def fsPath(*asPathSections):
  if len(asPathSections) == 0:
    return u"\\\\?\\" + os.getcwdu();
  sPath = os.path.join(*[unicode(s) for s in asPathSections]);
  if sPath[:2] != u"\\\\": # Absolute or relative path to local drive
    sDrive, sPath = os.path.splitdrive(sPath);
    if sDrive is None:
      # No drive provided: use global CWD
      sDrive, sCWDPath = os.path.splitdrive(os.getcwdu());
    else:
      # Drive provided: use CWD for the specified drive
      sCWDPath = os.path.abspath(sDrive)[2:];
    if sPath[0] != u"\\":
      # Path is relative to CWD path
      sPath = os.path.join(sCWDPath, sPath);
    return u"\\\\?\\" + sDrive + os.path.normpath(sPath);
  if sPath[2] != "?":
    # UNC path "\\..." => "\\?\UNC\..."
    return u"\\\\?\\UNC\\" + os.path.normpath(sPath[2:]);
  return u"\\\\?\\" + os.path.normpath(sPath[4:]);

def fsParentPath(*asPathSections):
  return os.path.dirname(fsPath(*asPathSections));
def fsName(*asPathSections):
  return os.path.basename(fsPath(*asPathSections));
def ftFile_sName_and_sExtension(*asPathSections):
    asComponents = fsName(*asPathSections).rsplit(u".", 1);
    return (
      len(asComponents) == 1 and (asComponents[0], None)              # "abc"   => ("abc", None)
      or len(asComponents[0]) == 0 and (u"." + asComponents[1], None)  # ".abc"  => (".abc", None)
      or tuple(asComponents)                                          # "ab.c"  => ("ab", "c")
    );

def fsRelativePathFromTo(sFromPath, sToPath):
  return os.path.relpath(fsPath(sToPath), fsPath(sFromPath));

def fbIsFolder(*asPathSections, **dxArguments):
  ebResult = febIsFolder(*asPathSections, **dxArguments);
  if isinstance(ebResult, bool):
    return ebResult;
  raise ebResult;

def febIsFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections) + u"\\";
  for uPause in auPauses:
    try:
      return os.path.isdir(sPath);
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to check if folder %s exists, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  return os.path.isdir(sPath);

def fbIsFile(*asPathSections):
  return febIsFile(*asPathSections); # Will always return a boolean since fbRetryOnFailure is not set.
def febIsFile(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections);
  for uPause in auPauses:
    try:
      return os.path.isfile(sPath);
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to check if file %s exists, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  return os.path.isdir(sPath);

def fasReadChildNamesFromFolder(*asPathSections, **dxArguments):
  easResult = feasReadChildNamesFromFolder(*asPathSections, **dxArguments);
  if isinstance(easResult, list):
    return easResult;
  raise easResult;

def feasReadChildNamesFromFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections) + u"\\";
  for uPause in auPauses:
    try:
      if not os.path.isdir(sPath): break; # This is never going to work, exit this loop and try anyway to cause an exception
      return os.listdir(sPath);
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to read children from folder %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  return os.listdir(sPath);

def fbCreateFolder(*asPathSections, **dxArguments):
  ebResult = febCreateFolder(*asPathSections, **dxArguments);
  if isinstance(ebResult, bool):
    return ebResult;
  raise ebResult;

def febCreateFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections) + u"\\";
  for uPause in auPauses:
    try:
      if os.path.isdir(sPath):
        return False;
      os.makedirs(sPath);
      return True;
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to create folder %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  if os.path.isdir(sPath):
    return False;
  os.makedirs(sPath);
  return True;

def fbDeleteFolder(*asPathSections):
  return febDeleteFolder(*asPathSections); # Will always return a boolean since fbRetryOnFailure is not set.
def febDeleteFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections) + u"\\";
  for uPause in auPauses:
    ebChildrenDeleted = febDeleteChildrenFromFolder(*asPathSections, fbRetryOnFailure = fbRetryOnFailure);
    if not isinstance(ebChildrenDeleted, bool):
      return ebChildrenDeleted; # Return exception
    try:
      if not os.path.isdir(sPath):
        return False;
      os.rmdir(sPath);
      return True;
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to delete folder %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  if not os.path.isdir(sPath):
    return False;
  ebChildrenDeleted = febDeleteChildrenFromFolder(*asPathSections, fbRetryOnFailure = fbRetryOnFailure);
  if not isinstance(ebChildrenDeleted, bool):
    return ebChildrenDeleted; # Return exception
  os.rmdir(sPath);
  return True;

def fbDeleteChildrenFromFolder(*asPathSections, **dxArguments):
  ebResult = febDeleteChildrenFromFolder(*asPathSections, **dxArguments);
  if isinstance(ebResult, bool):
    return ebResult;
  raise ebResult;

def febDeleteChildrenFromFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections) + u"\\";
  # 1 Get files and sub-folders
  for uPause in auPauses:
    try:
      asChildNames = os.path.isdir(sPath) and os.listdir(sPath) or None;
      break;
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to read children of folder %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  else:
    asChildNames = os.path.isdir(sChildPath) and os.listdir(sPath) or None;
  if asChildNames is None:
    return False; # Folder does not exist, nothing deleted.
  
  bChildrenDeleted = False;
  # Delete files, sub-folders
  for sChildName in asChildNames:
    sChildPath = fsPath(sPath, sChildName);
    for uPause in auPauses:
      try:
        bIsFile = os.path.isfile(sChildPath);
        bIsFolder = os.path.isdir(sChildPath);
      except (OSError, WindowsError) as oException:
        if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
        print "Error %s while attempting to read type of %s, will retry in %d seconds" % (repr(oException), sChildPath, uPause);
        time.sleep(uPause);
        continue;
      if bIsFile:
        try:
          os.remove(sChildPath);
        except WindowsError as oException:
          if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
          print "Error %s while attempting to delete file %s, will retry in %d seconds" % (repr(oException), sChildPath, uPause);
          time.sleep(uPause);
        else:
          bChildrenDeleted = True;
          break;
      elif bIsFolder:
        ebChildrenDeleted = febDeleteChildrenFromFolder(sChildPath, fbRetryOnFailure = fbRetryOnFailure);
        if isinstance(ebChildrenDeleted, bool):
          bChildrenDeleted = ebChildrenDeleted;
        else:
          return ebChildrenDeleted;
        try:
          os.rmdir(sChildPath);
        except (OSError, WindowsError) as oException:
          if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
          print "Error %s while attempting to delete folder %s, will retry in %d seconds" % (repr(oException), sChildPath, uPause);
          time.sleep(uPause);
        else:
          bChildrenDeleted = True;
          break;
    else:
      # Failed after every timeout so far, final try without exception handling:
      if os.path.isfile(sChildPath):
        os.remove(sChildPath);
        bChildrenDeleted = True;
      elif os.path.isdir(sChildPath):
        if fbDeleteChildrenFromFolder(sChildPath, fbRetryOnFailure = fbRetryOnFailure):
          bChildrenDeleted = True;
        os.rmdir(sChildPath);
        bChildrenDeleted = True;
  return bChildrenDeleted;

def fbDeleteFile(*asPathSections, **dxArguments):
  ebResult = febDeleteFile(*asPathSections, **dxArguments);
  if isinstance(ebResult, bool):
    return ebResult;
  raise ebResult;

def febDeleteFile(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections);
  for uPause in auPauses:
    try:
      if not os.path.isfile(sPath):
        return False;
      os.remove(sPath);
      return True;
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to delete file %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  if not os.path.isfile(sPath):
    return False;
  os.remove(sPath);
  return True;

def fsReadDataFromFile(*asPathSections):
  return fesReadDataFromFile(*asPathSections); # Will always return a string since fbRetryOnFailure is not set.
def fesReadDataFromFile(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections);
  for uPause in auPauses:
    try:
      oFile = open(sPath, "rb");
      try:
        return oFile.read();
      finally:
        oFile.close();
    except (WindowsError, IOError) as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to read from file %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  oFile = open(sPath, "rb");
  try:
    return oFile.read();
  finally:
    oFile.close();

def fWriteDataToFile(*asPathSections, **dxArguments):
  eResult = feWriteDataToFile(*asPathSections, **dxArguments);
  if eResult is None:
    return 
  raise eResult;

def feWriteDataToFile(sData, *asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsPath(*asPathSections);
  for uPause in auPauses:
    try:
      oFile = open(sPath, "wb");
      try:
        oFile.write(sData);
      finally:
        oFile.close();
      return None;
    except (WindowsError, IOError) as oException:
      if isinstance(oException, IOError) and oException.args[0] == 22:
        # (22, "invalid mode ('wb') or filename") => The mode is correct, so the name must be wrong: update the error
        oException.args = (22, "Invalid file name %s" % sPath);
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return oException;
      print "Error %s while attempting to write to file %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  oFile = open(sPath, "wb");
  try:
    oFile.write(sData);
  except IOError as oException:
    if isinstance(oException, IOError) and oException.args[0] == 22:
      # (22, "invalid mode ('wb') or filename") => The mode is correct, so the name must be wrong: update the error
      oException.args = (22, "Invalid file name %s" % sPath);
    raise;
  finally:
    oFile.close();
  return None;
