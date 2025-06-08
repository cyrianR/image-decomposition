import os
from PIL import Image
import random

# This script creates a dataset for double exposed image decomposition :
# - takes basic images and crop them randomly to a fixed size
# - then compute the double exposure between cropped images
# - separate the dataset in training, validation and test sets


## PARAMETERS
input_dir = "/home/cycy/Documents/datasets/PISC/images"
output_dir = "/home/cycy/Documents/datasets/PISC/img_decomposition_dataset/less_big_dataset_cropped_128"
n_images = 17000            # Number of images to use in the input directory
image_size = 128            # Size of the cropped images,
                            # should be less than the minimum image size in the input directory    
n_crop_by_image = 1         # Number of random crops by image
n_double_exposure = 1       # Number of double exposure by cropped image, it
                            # has to be equal or less than n_crop_by_image*n_images
train_percent = 0.7         # Percentage of training images
val_percent = 0.15          # Percentage of validation images
test_percent = 0.15         # Percentage of test images



## UTILITY FUNCTIONS
def get_minimum_image_size(directory):
    min_width, min_height = float('inf'), float('inf')
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                min_width = min(min_width, width)
                min_height = min(min_height, height)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    return min_width, min_height 

def crop_and_save(image_path, output_dir, image_name, n_crop_by_image):
    with Image.open(image_path) as img:
        width, height = img.size
        for i in range(n_crop_by_image):
            x = random.randint(0, width - image_size - 1)
            y = random.randint(0, height - image_size - 1)
            cropped_img = img.crop((x, y, x + image_size, y + image_size))
            if image_path.endswith(".png"):
                cropped_img = cropped_img.convert("RGB")
            cropped_img.save(os.path.join(output_dir, f"{image_name}_{i}.jpg"))         



## CHECK PARAMETERS
# Check if the input and output directories exist
if not os.path.exists(input_dir):
    raise FileNotFoundError(f"Input path does not exist: {input_dir}")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Check if n_double_exposure is less than or equal to n_crop_by_image*n_images
if not n_double_exposure <= n_crop_by_image * n_images:
    raise ValueError(f"n_double_exposure should be less than or equal to n_crop_by_image*n_images, but got {n_double_exposure} > {n_crop_by_image*n_images}")

# Check if the image size is less than the minimum image size in the input directory
min_width, min_height = get_minimum_image_size(input_dir)
if min_width < image_size or min_height < image_size:
    raise ValueError(f"Image size {image_size} is larger than the minimum image size {min_width}x{min_height} in the input directory, image can not be cropped.")

# Check if the input directory contains enough images
if len(os.listdir(input_dir)) < n_images:
    raise ValueError(f"Not enough images in the input directory. Found {len(os.listdir(input_dir))}, but need {n_images}.")

# Check if the sum of train, validation and test percentages equals 1
if train_percent + val_percent + test_percent != 1.0:
    raise ValueError("The sum of train, validation and test percentages must equal 1.")



## CREATE DATASET
# Get n_images randomly from the input directory
image_names = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
valid_images = []
for image_name in image_names:
    file_path = os.path.join(input_dir, image_name)
    try:
        with Image.open(file_path) as img:
            img.verify()
            valid_images.append(image_name)
    except Exception as e:
        print(f"Invalid image file {file_path}: {e}")

if len(valid_images) < n_images:
    raise ValueError(f"Not enough valid images in the input directory. Found {len(valid_images)}, but need {n_images}.")

random.shuffle(valid_images)
selected_images = valid_images[:n_images]

# Separate the dataset into training, validation and test sets
train_images = selected_images[:int(train_percent * len(selected_images))]
val_images = selected_images[int(train_percent * len(selected_images)):int((train_percent+val_percent) * len(selected_images))]
test_images = selected_images[int((train_percent+val_percent) * len(selected_images)):]

# Create the output directories
train_dir = os.path.join(output_dir, "train")
val_dir = os.path.join(output_dir, "val")
test_dir = os.path.join(output_dir, "test")
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)
os.makedirs(os.path.join(train_dir, "double_exposure"), exist_ok=True)
os.makedirs(os.path.join(val_dir, "double_exposure"), exist_ok=True)
os.makedirs(os.path.join(test_dir, "double_exposure"), exist_ok=True)
os.makedirs(os.path.join(train_dir, "single_exposure"), exist_ok=True)
os.makedirs(os.path.join(val_dir, "single_exposure"), exist_ok=True)
os.makedirs(os.path.join(test_dir, "single_exposure"), exist_ok=True)

# Crop and save the cropped images
for image_name in train_images:
    image_path = os.path.join(input_dir, image_name)
    crop_and_save(image_path, os.path.join(train_dir, "single_exposure"), os.path.splitext(image_name)[0], n_crop_by_image)

for image_name in val_images:
    image_path = os.path.join(input_dir, image_name)
    crop_and_save(image_path, os.path.join(val_dir, "single_exposure"), os.path.splitext(image_name)[0], n_crop_by_image)

for image_name in test_images:
    image_path = os.path.join(input_dir, image_name)
    crop_and_save(image_path, os.path.join(test_dir, "single_exposure"), os.path.splitext(image_name)[0], n_crop_by_image)

# Create double exposure images
train_cropped_images = os.listdir(os.path.join(train_dir, "single_exposure"))
val_cropped_images = os.listdir(os.path.join(val_dir, "single_exposure"))
test_cropped_images = os.listdir(os.path.join(test_dir, "single_exposure"))

train_cropped_dict = {image: 0 for image in train_cropped_images}
val_cropped_dict = {image: 0 for image in val_cropped_images}
test_cropped_dict = {image: 0 for image in test_cropped_images}

while train_cropped_images:
    image1 = random.choice(train_cropped_images)
    image2 = random.choice(train_cropped_images)
    if image1 != image2:
        img1_path = os.path.join(train_dir, "single_exposure", image1)
        img2_path = os.path.join(train_dir, "single_exposure", image2)
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)
        if img1.mode != "RGB":
            img1 = img1.convert("RGB")
        if img2.mode != "RGB":
            img2 = img2.convert("RGB")
        double_exposure = Image.blend(img1, img2, alpha=0.5)
        image1_name = os.path.splitext(image1)[0]
        image2_name = os.path.splitext(image2)[0]
        double_exposure.save(os.path.join(train_dir, "double_exposure", f"blend_{image1_name}-{image2_name}.jpg"))
        train_cropped_dict[image1] += 1
        train_cropped_dict[image2] += 1
        if train_cropped_dict[image1] >= n_double_exposure:
            train_cropped_images.remove(image1)
        if train_cropped_dict[image2] >= n_double_exposure:
            train_cropped_images.remove(image2)
    if len(train_cropped_images) == 1:
        print("Not enough images in training set to create double exposure, a double exposure was skipped.")
        break

while val_cropped_images:
    image1 = random.choice(val_cropped_images)
    image2 = random.choice(val_cropped_images)
    if image1 != image2:
        img1_path = os.path.join(val_dir, "single_exposure", image1)
        img2_path = os.path.join(val_dir, "single_exposure", image2)
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)
        if img1.mode != "RGB":
            img1 = img1.convert("RGB")
        if img2.mode != "RGB":
            img2 = img2.convert("RGB")
        double_exposure = Image.blend(img1, img2, alpha=0.5)
        image1_name = os.path.splitext(image1)[0]
        image2_name = os.path.splitext(image2)[0]
        double_exposure.save(os.path.join(val_dir, "double_exposure", f"blend_{image1_name}-{image2_name}.jpg"))
        val_cropped_dict[image1] += 1
        val_cropped_dict[image2] += 1
        if val_cropped_dict[image1] >= n_double_exposure:
            val_cropped_images.remove(image1)
        if val_cropped_dict[image2] >= n_double_exposure:
            val_cropped_images.remove(image2)
    if len(val_cropped_images) == 1:
        print("Not enough images in validation set to create double exposure, a double exposure was skipped.")
        break

while test_cropped_images:
    image1 = random.choice(test_cropped_images)
    image2 = random.choice(test_cropped_images)
    if image1 != image2:
        img1_path = os.path.join(test_dir, "single_exposure", image1)
        img2_path = os.path.join(test_dir, "single_exposure", image2)
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)
        if img1.mode != "RGB":
            img1 = img1.convert("RGB")
        if img2.mode != "RGB":
            img2 = img2.convert("RGB")
        double_exposure = Image.blend(img1, img2, alpha=0.5)
        image1_name = os.path.splitext(image1)[0]
        image2_name = os.path.splitext(image2)[0]
        double_exposure.save(os.path.join(test_dir, "double_exposure", f"blend_{image1_name}-{image2_name}.jpg"))
        test_cropped_dict[image1] += 1
        test_cropped_dict[image2] += 1
        if test_cropped_dict[image1] >= n_double_exposure:
            test_cropped_images.remove(image1)
        if test_cropped_dict[image2] >= n_double_exposure:
            test_cropped_images.remove(image2)
    if len(test_cropped_images) == 1:
        print("Not enough images in test set to create double exposure, a double exposure was skipped.")
        break









