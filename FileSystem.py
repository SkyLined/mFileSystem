import os, shutil, time;

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

dsInvalidPathCharacterTranslationMap = {
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

def fsTranslateToValidName(sName):
  return u"".join([dsInvalidPathCharacterTranslationMap.get(sChar, sChar) for sChar in unicode(sName)]);

def fsFullPath(*asPathSections):
  # http://msdn.microsoft.com/en-us/gozerlib.ary/aa365247.aspx
  sPath = unicode(os.path.join(*asPathSections));
  if sPath[:2] == u"\\\\": return sPath;
  assert sPath[1] == u":", "Only full paths are acceptable, not %s" % sPath;
  return u"\\\\?\\" + sPath;

def fsFullParentPath(*asPathSections):
  return os.path.dirname(fsFullPath(*asPathSections));
def fsName(*asPathSections):
  return os.path.basename(fsFullPath(*asPathSections));
def ftFile_sName_and_sExtension(*asPathSections):
    asComponents = fsName(*asPathSections).rsplit(u".", 1);
    return (
      len(asComponents) == 1 and (asComponents[0], None)              # "abc"   => ("abc", None)
      or len(asComponents[0]) == 0 and (u"." + asComponents[1], None)  # ".abc"  => (".abc", None)
      or tuple(asComponents)                                          # "ab.c"  => ("ab", "c")
    );

def fsRelativePathFromTo(sFromPath, sToPath):
  return os.path.relpath(fsFullPath(sToPath), fsFullPath(sFromPath));

def fbIsFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections) + u"\\";
  for uPause in auPauses:
    try:
      return os.path.isdir(sPath);
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return None;
      print "Error %s while attempting to check if folder %s exists, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  return os.path.isdir(sPath);

def fbIsFile(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections);
  for uPause in auPauses:
    try:
      return os.path.isfile(sPath);
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return None;
      print "Error %s while attempting to check if file %s exists, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  return os.path.isdir(sPath);

def fasReadChildNamesFromFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections) + u"\\";
  for uPause in auPauses:
    try:
      if not os.path.isdir(sPath): break; # This is never going to work, exit this loop and try anyway to cause an exception
      return os.listdir(sPath);
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return None;
      print "Error %s while attempting to read children from folder %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  return os.listdir(sPath);

def fbCreateFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections) + u"\\";
  for uPause in auPauses:
    try:
      if not os.path.isdir(sPath): os.makedirs(sPath);
      return True;
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return False;
      print "Error %s while attempting to create folder %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  if not os.path.isdir(sPath): os.makedirs(sPath);
  return True;

def fbDeleteFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections) + u"\\";
  for uPause in auPauses:
    fbDeleteChildrenFromFolder(sPath, fbRetryOnFailure = fbRetryOnFailure);
    try:
      if os.path.isdir(sPath):
        os.rmdir(sPath);
        return True;
      return False;
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return False;
      print "Error %s while attempting to delete folder %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  if os.path.isdir(sPath):
    fbDeleteChildrenFromFolder(sPath, fbRetryOnFailure = fbRetryOnFailure);
    os.rmdir(sPath);
    return True;
  return False;
fbRemoveFolder = fbDeleteFolder;

def fbDeleteChildrenFromFolder(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections) + u"\\";
  bChildrenDeleted = False;
  # 1 Get files and sub-folders
  for uPause in auPauses:
    try:
      asChildNames = os.path.isdir(sPath) and os.listdir(sPath) or None;
      break;
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return False;
      print "Error %s while attempting to read children of folder %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  else:
    asChildNames = os.path.isdir(sChildPath) and os.listdir(sPath) or None;
  if asChildNames is None:
    return bChildrenDeleted; # Folder does not exist, nothing deleted.
  
  # Delete files, sub-folders
  for sChildName in asChildNames:
    sChildPath = fsFullPath(sPath, sChildName);
    for uPause in auPauses:
      try:
        bIsFile = os.path.isfile(sChildPath);
        bIsFolder = os.path.isdir(sChildPath);
      except (OSError, WindowsError) as oException:
        if fbRetryOnFailure is not None and not fbRetryOnFailure(): return False;
        print "Error %s while attempting to read type of %s, will retry in %d seconds" % (repr(oException), sChildPath, uPause);
        time.sleep(uPause);
        continue;
      if bIsFile:
        try:
          os.remove(sChildPath);
        except WindowsError as oException:
          if fbRetryOnFailure is not None and not fbRetryOnFailure(): return False;
          print "Error %s while attempting to delete file %s, will retry in %d seconds" % (repr(oException), sChildPath, uPause);
          time.sleep(uPause);
        else:
          bChildrenDeleted = True;
          break;
      elif bIsFolder:
        if fbDeleteChildrenFromFolder(sChildPath, fbRetryOnFailure = fbRetryOnFailure):
          bChildrenDeleted = True;
        try:
          os.rmdir(sChildPath);
        except (OSError, WindowsError) as oException:
          if fbRetryOnFailure is not None and not fbRetryOnFailure(): return False;
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
fbRemoveChildrenFromFolder = fbDeleteChildrenFromFolder;

def fbDeleteFile(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections);
  for uPause in auPauses:
    try:
      if os.path.isfile(sPath): os.remove(sPath);
      return True;
    except WindowsError as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return False;
      print "Error %s while attempting to delete file %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  if os.path.isfile(sPath): os.remove(sPath);
  return True;

def fsReadDataFromFile(*asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections);
  for uPause in auPauses:
    try:
      oFile = open(sPath, "rb");
      try:
        return oFile.read();
      finally:
        oFile.close();
    except (WindowsError, IOError) as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return None;
      print "Error %s while attempting to read from file %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  oFile = open(sPath, "rb");
  try:
    return oFile.read();
  finally:
    oFile.close();

def fbWriteDataToFile(sData, *asPathSections, **dxArguments):
  fbRetryOnFailure = dxArguments.get("fbRetryOnFailure");
  sPath = fsFullPath(*asPathSections);
  for uPause in auPauses:
    try:
      oFile = open(sPath, "wb");
      try:
        oFile.write(sData);
      finally:
        oFile.close();
      return True;
    except (WindowsError, IOError) as oException:
      if fbRetryOnFailure is not None and not fbRetryOnFailure(): return False;
      print "Error %s while attempting to write to file %s, will retry in %d seconds" % (repr(oException), sPath, uPause);
      time.sleep(uPause);
  oFile = open(sPath, "wb");
  try:
    oFile.write(sData);
  finally:
    oFile.close();
  return True;
