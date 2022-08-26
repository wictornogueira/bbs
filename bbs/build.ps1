# Define optional flags
param (
	[switch] $d	  # Generate dist file
)

$baseDir = $pwd
$binDir = "$baseDir\bin"
$buildDir = "$binDir\Release"
$tempDir = "$binDir\temp"
$distDir = "$baseDir\..\dist"

$pythonVer = "38"
$pythonURL = "https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-win32.zip"

# Create dist file
if ($d) {
	# Create temp dir
	New-Item -ItemType Directory -Force -Path "$tempDir\scripts\bbs\natives" | Out-Null

	# Download and copy python whatevies
	Invoke-WebRequest -Uri $pythonURL -OutFile "$tempDir\python.zip"
	Expand-Archive -Force -Path "$tempDir\python.zip" -Destination "$tempDir\scripts\bbs\natives" | Out-Null

	Move-Item -Force "$tempDir\scripts\bbs\natives\python$pythonVer.dll" -Destination "$tempDir\"
	Move-Item -Force "$tempDir\scripts\bbs\natives\python$pythonVer.zip" -Destination "$tempDir\"

	Remove-Item -Force -Path "$tempDir\scripts\bbs\natives\*" -Include *.exe | Out-Null
	Remove-Item -Force -Path "$tempDir\python.zip" | Out-Null

	# Copy bbs.asi
	Copy-Item -Force "$buildDir\bbs.asi" -Destination "$tempDir\scripts"

	# Copy std
	Copy-Item -Force "$baseDir\..\std\*" -Destination "$tempDir\scripts\bbs" -Recurse

	# Create dist dir
	New-Item -ItemType Directory -Force -Path "$distDir\" | Out-Null
	# Zip files
	Compress-Archive -Force -Path "$tempDir\*" -DestinationPath "$distDir\bbs.zip"

	# Delete temp dir
	Remove-Item -Force -Recurse -Path "$tempDir"
}
