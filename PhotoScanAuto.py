import os
import PhotoScan

doc = PhotoScan.app.document
print("Script started")

chunk = PhotoScan.Chunk()
chunk.label = "Multiframe"
doc.chunks.add(chunk)

path = PhotoScan.app.getExistingDirectory("main folder:")
folders = os.listdir(path)

for folder in list(folders):
    if not os.path.isdir(path + "\\" + folder):
        folders.remove(folder)
folders.sort()

image_folders = list()
for frame in range(len(folders)):
    images = os.listdir(path + "\\" + folders[frame])
    for image in list(images):
        if image.rsplit(".", 1)[1].upper() != "JPG":
            images.remove(image)
    images.sort()
    image_folders.append(images.copy())

frames = len(image_folders[0])

# Loading images:
for frame in range(frames):

    for folder in range(len(folders)):
        if not frame:
            chunk.photos.add(path + "\\" + folders[folder] + "\\" + image_folders[folder][frame])
        else:
            f = PhotoScan.Frame()
            f.open(path + "\\" + folders[folder] + "\\" + image_folders[folder][frame], 0)
            chunk.photos[folder].frames.append(f)
doc.activeChunk = chunk

# Processing:
chunk.matchPhotos(accuracy='high', preselection='disabled', filter_mask=False, point_limit=40000)
chunk.alignPhotos()

chunk.buildDenseCloud(quality='medium', filter='aggressive', gpu_mask=1, cpu_cores_inactive=1,
                      frames=list(range(frames)))
chunk.buildModel(surface='arbitrary', source='dense', interpolation='enabled', faces=200000, frames=list(range(frames)))

# chunk.buildTexture(mapping = 'generic', blending = 'mosaic', size = 2048, count=1, frames = list(range(frames)))

print("Script finished")