@echo off

SET ROOT_DIR=%~dp0
SET JAVA_HOME=%ROOT_DIR%..\jre\
SET H2DB_DIR=%~dp0
SET JAVA_EXE=%JAVA_HOME%bin\java.exe

cd %H2DB_DIR%

echo -----------------------------------------------------------------
%JAVA_EXE% -version
echo -----------------------------------------------------------------
%JAVA_EXE% -cp %H2DB_DIR%h2-1.4.197.jar org.h2.tools.Recover -dir %H2DB_DIR%
echo h2 database repaired
del %H2DB_DIR%historian_extractor.mv.txt
del %H2DB_DIR%historian_extractor.h2.sql
echo -----------------------------------------------------------------
