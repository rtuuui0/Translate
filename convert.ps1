# PowerShell script to convert Chinese characters in values to Unicode escape sequences

$inputFile = '.\chinese_translation.txt'
$outputFile = '.\chinese_unicode.properties'

# Function to escape a string to Unicode
function Escape-ToUnicode {
    param([string]$text)
    $escaped = ""
    foreach ($char in $text.ToCharArray()) {
        $code = [int][char]$char
        $escaped += "\u" + $code.ToString("X4")
    }
    return $escaped
}

# Read the input file
$lines = Get-Content $inputFile -Encoding UTF8
Write-Host "Lines count: $($lines.Count)"

# Process each line
$processedLines = foreach ($line in $lines) {
    if ($line -match '^([^=]+)=(.*)$') {
        $key = $matches[1]
        $value = $matches[2]
        $escapedValue = Escape-ToUnicode $value
        "$key=$escapedValue"
    } else {
        $line
    }
}

# Write to output file
Write-Host "Processed lines count: $($processedLines.Count)"
$processedLines | Out-File $outputFile -Encoding UTF8

Write-Host "Conversion completed. Output file: $outputFile"