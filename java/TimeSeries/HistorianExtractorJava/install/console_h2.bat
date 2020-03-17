@echo off

SET ROOT_DIR=%~dp0
SET JAVA_HOME=%ROOT_DIR%jre\
SET PATH=%JAVA_HOME%bin;%PATH%
SET LIBPATH=%ROOT_DIR%lib
SET JAVA_EXE=%JAVA_HOME%bin\java.exe
SET JAVA_OPTION=-Djava.library.path=%LIBPATH% -Dlogback.configurationFile=%ROOT_DIR%logback.xml

cd %ROOT_DIR%

echo -----------------------------------------------------------------
%JAVA_EXE% -version
echo -----------------------------------------------------------------
%JAVA_EXE% %JAVA_OPTION% -jar historian-extractor.jar -mode CONSOLE
echo -----------------------------------------------------------------
