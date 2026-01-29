# Blind-Spot Collision Detection Experimental Data

This repository contains the **experimental data** used to evaluate the effectiveness of a **Blind-Spot Collision Detection System**. The system is designed to detect vehicles or pedestrians in the driver's blind-spot and provide appropriate alerts to ensure safety.

## Description

The goal of the project was to assess the accuracy of the **Blind-Spot Object Detection System** by analyzing 10,000 frames of real-time camera data. The frames were captured from a live camera feed monitoring the road area around the vehicle for **10 minutes**. The system categorizes objects in the blind-spot into four categories:

- **True Positives (TP)**: The system correctly detects vehicles or pedestrians in the blind-spot and issues appropriate alerts.
- **True Negatives (TN)**: No objects are present, and the system does not issue unnecessary alerts.
- **False Positives (FP)**: The system mistakenly identifies background elements (e.g., trees, shadows, etc.) as obstacles, leading to unnecessary alerts.
- **False Negatives (FN)**: The system fails to detect actual vehicles or pedestrians, potentially compromising safety.

## Data Overview

The dataset contains **10,000 frames** captured from the live camera feed. Each frame is annotated with the following categories:

- **TP**: True Positive (object detected accurately)
- **FP**: False Positive (background mistakenly detected as object)
- **TN**: True Negative (no object, no alert)
- **FN**: False Negative (failure to detect an object)

The data was evaluated to test the performance of the system in detecting potentially dangerous objects in the blind-spot.

## Data Structure

The dataset consists of a CSV file where each frame is represented by the following columns:

- **frame**: Frame number (from 1 to 10,000)
- **TP**: Number of True Positive detections
- **FP**: Number of False Positive detections
- **FN**: Number of False Negative detections
- **TN**: Number of True Negative detections

### Example of Data Row

| frame | TP | FP | FN | TN |
|-------|----|----|----|----|
| 1     | 8  | 1  | 0  | 1  |
| 2     | 3  | 0  | 0  | 0  |
| 3     | 2  | 0  | 0  | 0  |
| ...   | ...| ...| ...| ...|

## Metrics

The performance of the system is evaluated based on the following metrics:

- **Precision**: The proportion of correct positive detections (TP) over all positive predictions (TP + FP).
- **Recall**: The proportion of correct positive detections (TP) over all actual positive cases (TP + FN).
- **F1 Score**: The harmonic mean of precision and recall, providing a balance between both metrics.
- **Confusion Matrix**: A matrix used to summarize the performance of the system. The matrix is normalized to show the proportion of True Positives, False Positives, False Negatives, and True Negatives.

## Data Access

You can download the experimental data in CSV format directly from the repository. The data includes all frames, with the corresponding annotations for TP, FP, FN, and TN.

- **CSV file path**: `experimental_frames.csv`

## How to Use

### Prerequisites

To use this dataset, you should have **Python 3** and the following libraries installed:

- **pandas**: for handling data.
- **numpy**: for numerical operations.

You can install the necessary packages using:

```bash
pip install pandas numpy
