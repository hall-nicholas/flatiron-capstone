# Rolling Shutter Distortion Detection
##### by Nicholas Hall

<br/>

<img src='images/zeroeyes-logo.png'/>

<br/>

## Business Objective:
<b/>Identify rolling shutter distortion for ZeroEyes' use in their data pipeline.</b>

<br/>

# Project Setup
## 1. Folder Creation

First, some empty folders must be manually created for the code to work.
- `flatiron-capstone/data`
- `flatiron-capstone/models`
- `flatiron-capstone/created_data`
- `flatiron-capstone/created_data/test`
- `flatiron-capstone/created_data/test/NORMAL`
- `flatiron-capstone/created_data/test/ROLLING_SHUTTER`
- `flatiron-capstone/created_data/train`
- `flatiron-capstone/created_data/train/NORMAL`
- `flatiron-capstone/created_data/train/ROLLING_SHUTTER`

## 2. Data Download
The following COCO files must be downloaded:
<ul/>
    <li/><a/ href='http://images.cocodataset.org/zips/train2017.zip'>2017 Train images</a></li>
    <li/><a/ href='http://images.cocodataset.org/zips/val2017.zip'>2017 Val images</a></li>
    <li/><a/ href='http://images.cocodataset.org/annotations/annotations_trainval2017.zip'>2017 Train/Val annotations</a></li>
</ul>
In case the above links do not work, these files can be downloaded from <a href="https://cocodataset.org/#download"/>the COCO website</a>. 

<br/>

Afterwards, the contents of the `.zip` files should be extracted to the `flatiron-capstone/data/` directory.

## 3. Environment Setup

Lastly, an included `.yml` file has been included with all packages needed to run any script or notebook in this project, and can be installed using Anaconda.

<br/>

# Project Overview
## What is ZeroEyes?
ZeroEyes, the company that I work for, provides a service that uses artificial intelligence
to identify, prevent & mitigate active shooter situations using pre-existing surveillance
cameras. It incorporates a robust, multilayered approach including a human-in-the-loop 
element to prevent false positives and to coordinate with law enforcement and first responders 
in case of a true active shooter scenario. They monitor thousands of cameras nationwide
in both public and private buildings, and I wanted to develop a tool that they could
potentially use to eliminate some distortion and make every camera frame valuable.

## What is rolling shutter distortion?
A rolling shutter is one of two main types of shutters found in both consumer
and commercial cameras. While cameras with global shutters capture all pixels simultaneously,
this type of camera typically offers a lower frame rate compared to a similarly
priced rolling shutter camera. And while rolling shutter cameras have a higher
frame rate, they capture all pixels sequentially, which, when capturing fast-moving objects, can cause what is known as "rolling shutter distortion".

<br/>

<img src='images/rolling-shutter-distortion-example-1.jpg'/>

<br/>

<img src='images/rolling-shutter-distortion-example-2.jpg'/>

<br/>

So: why should ZeroEyes care? Well, since ZeroEyes is camera agnostic, it operates on
thousands of this type of camera already, which is susceptible to this distortion and
can modify the appearance of objects and impact the ability to detect said objects. In
the context of ZeroEyes, every second and every frame matters. Identifying when and where
rolling shutter distortion occurs could potentially mean the difference between life and
death.

For example, if a shooter is caught running down a hallway, swiftly rotating their body, 
or riding in a fast-moving vehicle, eliminating this distortion is paramount.

So, I set out to create a tool to detect rolling shutter distortion. Some potential use
cases for this tool include:
- Use it in the first step in a process to attempt to correct this distortion
- Identify cameras that often produce images with rolling shutter distortion.

## Data:
Unfortunately, there is no readily available data on rolling shutter distortion.
Consequently, I had to synthesize my own by applying a custom rolling shutter effect.

<br/>

### <i/>Example transformation:</i>

Before:

<img src='images/data-synthesis-example-before.png'/>

<br/>

After:

<img src='images/data-synthesis-example-after.png'/>

<br/>

Using the COCO 2017 dataset, I was able to create a new dataset using a built-from-scratch
rolling shutter effect. Using people as the target for my model, I extracted polygonal
segmentation annotations provided by COCO and applied the rolling shutter effect to the area
within the segmentaion.

One of the advantages of using COCO is that it is a very large dataset, containing over
330,000 images in total, 200,000 of which are annotated. For the purposes of my project,
since not every image included a person in it, I had about 70,000 images to work with.

Another advantage is that it is well-known and oft-used dataset, and is widely-regarded as a 
benchmark for machine learning algorithms.

However, there are some limitations to this dataset. The annotation boundaries are often
imprecise. For example, the polygonal segmentation annotations provided typically do not
capture all the pixels of any given object, which introduces additional distortion of its 
own in the data synthesis process. Further, some annotations are outright inaccurate.

## Model Evaluation:

<br/>

<img src='images/model-evaluation.png'/>

<br/>

Unfortunately, none of the models I produced performed extraordinarily well, which I attribute
to the complexity of the task set forth. To achieve better results, I would likely need to train 
the model for longer and on a wider range of data. That said, the MobileNetV3Large model managed
to eke out a better performance than other simpler models, indicating that the model was able
to recognize some elements of the distortion effect, if not in full.

## Conclusions, Limitations, & Future Recommendations:
So, while this is a promising tool, it is suitable only as a proof of concept until tested on 
real-world rolling shutter distortion data. Additionally, inaccurate and imprecise COCO annotations
hampered the data synthesis process introducing additional, unrelated distortion. Lastly, pre-existing 
distortion within the COCO dataset was unaccounted for as there was no way for me to isolate
this distortion save for manually combing through thousands of images.

For some future recommendations for continuing this project, I'd like to implement various neural network
architectures to achieve better metric scores. I'd also like to obtain more accurately annotated
data to synthesize on-- or better yet, collect real data to train on. The last recommendations I have 
are to investigate synthesizing the distortion that occurs when swiftly-rotating objects are captured
on rolling shutter cameras, as well as to explore with locating and reversing this distortion in an
attempt to repair the image.