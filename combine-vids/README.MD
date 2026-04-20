# Combine Videos

Small Tkinter GUI for combining multiple video files with ffmpeg using the concat demuxer and stream copy mode, which matches the no-reencode approach from the linked ffmpeg method.

## Requirements

- Python 3.14+
- ffmpeg installed and available on PATH

## Install ffmpeg On Windows

Install ffmpeg with winget:

```powershell
winget install --id Gyan.FFmpeg.Shared -e --source winget
```

If `ffmpeg` is not recognized after installation, add its `bin` folder to your PATH.

Typical steps on Windows:

1. Open Start and search for `Edit the system environment variables`.
2. Click `Environment Variables...`.
3. Under `User variables` or `System variables`, select `Path` and click `Edit`.
4. Click `New` and add the ffmpeg `bin` folder path.
5. Click `OK` on all dialogs and restart any open terminals.

Common install location example:

```text
C:\Program Files\FFmpeg\bin
```

Then verify it works:

```powershell
ffmpeg -version
```

## Run

```powershell
python .\combine-vids.py
```

## Usage

1. Add two or more video files.
2. Reorder them with Move Up and Move Down if needed.
3. Choose the output folder with Browse.
4. Enter the output filename.
5. Click Combine Videos.

This uses:

```text
ffmpeg -f concat -safe 0 -i <file-list> -c copy <output>
```

The input files must be compatible for stream copying, which usually means matching codecs, container expectations, and stream layout.
