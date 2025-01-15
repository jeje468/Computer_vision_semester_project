import numpy as np
import cv2

def calibrateCamera():
    dirname = "Images/Calibration_images/"
    img_names = [dirname + str(i) + ".jpg" for i in range(20)]

    pattern_size = (8,6)

    square_size = 25 
    indices = np.indices(pattern_size, dtype=np.float32)

    indices *= square_size

    coords_3D = np.transpose(indices, [2, 1, 0])

    coords_3D = coords_3D.reshape(-1, 2)

    pattern_points = np.concatenate([coords_3D, np.zeros([coords_3D.shape[0], 1], dtype=np.float32)], axis=-1)

    def processImage(fn):
        print('processing {}'.format(fn))
        img = cv2.imread(fn, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print("Failed to load", fn)
            return None
        found, corners = cv2.findChessboardCorners(img, pattern_size)
        if found:
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 5, 1)
            cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
        else:
            print('chessboard not found')
            return None
        print('           %s... OK' % fn)
        return (corners.reshape(-1, 2), pattern_points)


    chessboards = [processImage(fn) for fn in img_names]
    chessboards = [x for x in chessboards if x is not None]

    obj_points = [] 
    img_points = [] 

    for (corners, pattern_points) in chessboards:
            img_points.append(corners)
            obj_points.append(pattern_points)

    h, w = cv2.imread(img_names[0], cv2.IMREAD_GRAYSCALE).shape[:2]

    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h), None, None)

    rotation_matrix = cv2.Rodrigues(rvecs[0])[0]
    translation_matrix = tvecs[0]
    extrinsic_matrix = np.concatenate([rotation_matrix,translation_matrix], axis=1)

    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

    return camera_matrix, dist_coefs, newcameramtx, roi

def undistortImage(img, camera_matrix, dist_coefs, newcameramtx, roi):
    im_undistorted = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

    x, y, w_2, h_2 = roi
    im_undistorted = im_undistorted[y:y+h_2, x:x+w_2]

    return im_undistorted
