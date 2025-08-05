import os
import numpy as np
from skimage import draw
import pydicom


def load_ct_images(ct_folder):
    """Load CT DICOM images, convert to HU, and return a 3D numpy array."""
    slices = []
    for filename in sorted(os.listdir(ct_folder)):
        if filename.endswith('.dcm'):
            dicom = pydicom.dcmread(os.path.join(ct_folder, filename))
            slices.append(dicom)
    
    # Sort slices based on the Image Position Patient to get correct slice order
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    
    # Get pixel data and scaling factors
    image_data = np.stack([s.pixel_array for s in slices], axis=-1)
    
    # Convert to Hounsfield Units (HU)
    rescale_slope = slices[0].RescaleSlope if 'RescaleSlope' in slices[0] else 1
    rescale_intercept = slices[0].RescaleIntercept if 'RescaleIntercept' in slices[0] else 0

    hu_image = image_data * rescale_slope + rescale_intercept

    # Get pixel spacing and origin
    pixel_spacing = list(slices[0].PixelSpacing)  # Convert MultiValue to list
    slice_thickness = float(slices[0].SliceThickness)  # Ensure this is a float
    pixel_spacing.append(slice_thickness)  # Now it's safe to append
    
    origin = slices[0].ImagePositionPatient  # Origin of the first slice in mm
    
    return hu_image, pixel_spacing, origin

def load_rtstruct(rtstruct_path, roi_name):
    """Load RTSTRUCT file and return contour data for 'Heart'."""
    rtstruct = pydicom.dcmread(rtstruct_path)
    
    for roi in rtstruct.StructureSetROISequence:
        if roi.ROIName == f"{roi_name}":
            roi_number = roi.ROINumber
            break
    
    for contour in rtstruct.ROIContourSequence:
        if contour.ReferencedROINumber == roi_number:
            heart_contours = contour.ContourSequence
            break
    return heart_contours

def get_mask_from_contours(ct_folder, rtstruct_path, roi_name):
    """Convert contours into a binary mask."""
    ct_image, pixel_spacing, origin = load_ct_images(ct_folder)
    contours = load_rtstruct(rtstruct_path, roi_name)
    image_shape = ct_image.shape
    
    mask = np.zeros(image_shape, dtype=np.uint8)
    
    # Loop through each contour in the RTSTRUCT file
    for contour in contours:
        # Contour points are in physical space (mm), we need to convert them to voxel indices
        contour_points = np.array(contour.ContourData).reshape(-1, 3)

        # Convert contour points from DICOM physical coordinates (mm) to voxel coordinates
        x_coords = (contour_points[:, 0] - origin[0]) / pixel_spacing[0]
        y_coords = (contour_points[:, 1] - origin[1]) / pixel_spacing[1]
        
        # Find the z-index (slice index) by comparing z position to the slice positions
        z_pos = contour_points[0, 2]  # Z-coordinate (all points in one contour are in one slice)
        z_index = int(round((z_pos - origin[2]) / pixel_spacing[2]))

        # Ensure z_index is within bounds
        if z_index < 0 or z_index >= image_shape[2]:
            continue

        # Get integer pixel coordinates from physical coordinates
        rr, cc = draw.polygon(y_coords, x_coords, shape=image_shape[:2])

        # Apply the mask for this specific slice
        mask[rr, cc, z_index] = 1

    return ct_image, mask, pixel_spacing