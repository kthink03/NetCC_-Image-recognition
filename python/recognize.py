import cv2
import numpy as np

# open video file
video_path = 'gps.mp4'
cap = cv2.VideoCapture(video_path)

# output_size = (375, 667) # (width, height)
# fit_to = 'height'

# initialize writing video
# fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
# out = cv2.VideoWriter('%s_output.mp4' % (video_path.split('.')[0]), fourcc, cap.get(cv2.CAP_PROP_FPS), output_size)

# check file is opened
if not cap.isOpened():
    exit()

# initialize tracker
OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

# global variables
top_bottom_list, left_right_list = [], []

# main
ret, img_tmp = cap.read()
img = cv2.transpose(img_tmp)
img = cv2.flip(img, 1)
frame=img.read()

cv2.namedWindow('Select Window')
cv2.imshow('Select Window', img)

# select ROI, 사각 선택후 스페이스 바 누르기
# rect = cv2.selectROI('Select Window', img, fromCenter=False, showCrosshair=True) #rect = (x, y, 가로길이, 세로길이)
cv2.destroyWindow('Select Window')

point = []
count = 0


def tracking(tracker, num):
    global count
    # count += 1
    # read frame from video
    ret, img_tmp = cap.read()
    img = cv2.transpose(img_tmp)
    img = cv2.flip(img, 1)

    if not ret:
        exit()

    # update tracker and get position from new frame
    success, box = tracker.update(img)
    # if success:
    left, top, w, h = [int(v) for v in box]
    right = left + w
    bottom = top + h

    # save sizes of image
    top_bottom_list.append(np.array([top, bottom]))
    left_right_list.append(np.array([left, right]))

    # use recent 10 elements for crop (window_size=10)
    if len(top_bottom_list) > 10:
        del top_bottom_list[0]
        del left_right_list[0]

    # compute moving average
    avg_height_range = np.mean(top_bottom_list, axis=0).astype(np.int)
    avg_width_range = np.mean(left_right_list, axis=0).astype(np.int)
    avg_center = np.array([np.mean(avg_width_range), np.mean(avg_height_range)])  # (x, y)

    # compute scaled width and height
    scale = 1.3
    avg_height = (avg_height_range[1] - avg_height_range[0]) * scale
    avg_width = (avg_width_range[1] - avg_width_range[0]) * scale

    # compute new scaled ROI
    avg_height_range = np.array([avg_center[1] - avg_height / 2, avg_center[1] + avg_height / 2])
    avg_width_range = np.array([avg_center[0] - avg_width / 2, avg_center[0] + avg_width / 2])
    '''
  # fit to output aspect ratio
  if fit_to == 'width':
    avg_height_range = np.array([
      avg_center[1] - avg_width * output_size[1] / output_size[0] / 2,
      avg_center[1] + avg_width * output_size[1] / output_size[0] / 2
    ]).astype(np.int).clip(0, 9999)

    avg_width_range = avg_width_range.astype(np.int).clip(0, 9999)
  elif fit_to == 'height':
    avg_height_range = avg_height_range.astype(np.int).clip(0, 9999)

    avg_width_range = np.array([
      avg_center[0] - avg_height * output_size[0] / output_size[1] / 2,
      avg_center[0] + avg_height * output_size[0] / output_size[1] / 2
    ]).astype(np.int).clip(0, 9999)

  # crop image
  result_img = img[avg_height_range[0]:avg_height_range[1], avg_width_range[0]:avg_width_range[1]].copy()

  # resize image to output size
  result_img = cv2.resize(result_img, output_size)
  '''
    # visualize
    pt1 = (int(left), int(top))
    pt2 = (int(right), int(bottom))
    pt = [pt1, pt2]

    if count < 4:
        point.append(pt1)
        point.append(pt2)
        count = count + 1

    else:
        point[2 * num] = pt1
        point[2 * num + 1] = pt2

    i = 0
    print(point)
    length = len(point) / 2
    print(length)
    for i in range(int(length)):
        cv2.rectangle(img, point[2 * i], point[2 * i + 1], (255, 255, 255), 3)

    cv2.imshow('img', img)


rect = []
tracker = []

rect.append((198, 463, 20, 65))
rect.append((305, 466, 24, 53))
rect.append((239, 413, 20, 52))
rect.append((287, 392, 20, 48))

tracker.append(OPENCV_OBJECT_TRACKERS['csrt']())
tracker.append(OPENCV_OBJECT_TRACKERS['csrt']())
tracker.append(OPENCV_OBJECT_TRACKERS['csrt']())
tracker.append(OPENCV_OBJECT_TRACKERS['csrt']())

tracker[0].init(img, rect[0])
tracker[1].init(img, rect[1])
tracker[2].init(img, rect[2])
tracker[3].init(img, rect[3])

while True:

    i = 0
    for i in range(4):
        tracking(tracker[i], i)

    # cv2.imshow('img', img)
    # cv2.imshow('result', result_img)
    # write video
    # out.write(result_img)
    if cv2.waitKey(1) == ord('q'):
        break

# release everything
cap.release()
# out.release()
cv2.destroyAllWindows()