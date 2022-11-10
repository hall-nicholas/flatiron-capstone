# Rolling Shutter Distortion Detection
##### by Nicholas Hall

## Business Objective:
Identify rolling shutter distortion for ZeroEyes' use in their data pipeline.

## Data:
Modified version of the COCO 2017 dataset. Modifications automatically made by code in the final notebook-- "2017 Train images", "2017 Val images", and "2017 Train/Val annotations" should be downloaded from <a href="https://cocodataset.org/#download"/>the COCO website</a> and placed in the `flatiron-capstone/data/` directory.

## Metrics:
F1 score to emphasize importance of precision and recall

## Model:
Best model results in an F1 score of .62 (WIP)

## Future Considerations:
- Test/train on more real data
- Improve rolling shutter effect tool