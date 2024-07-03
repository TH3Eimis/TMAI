# created using tutorial from https://antonin.cool/trackmania-ia-deeplearning-python-opencv-self-driving/
# with modifications to fit the project

import cv2
import numpy as np
import pyautogui
from queue import Queue
from PIL import ImageGrab


def get_window_corners():
    window_title = "TrackMania Nations Forever (TMInterface 2.1.4.testing)"
    window = pyautogui.getWindowsWithTitle(window_title)
    
    if window:
        window = window[0]  
        window_x, window_y, window_width, window_height = window.left, window.top, window.width, window.height

        corners = {
                "top_left": (window_x, window_y),
                "top_right": (window_x + window_width, window_y),
                "bottom_left": (window_x, window_y + window_height),
                "bottom_right": (window_x + window_width, window_y + window_height)
        }
        print(f"window width: {window_width}, window height: {window_height}")
        return corners, window_width, window_height
    
def findRoi(img,HEIGHT,WIDTH):
    ROI_vertices = np.array([[0, HEIGHT * 0.48], # 1
                         [WIDTH / 3, HEIGHT * 0.43], # 2 
                         [WIDTH * 0.62, HEIGHT * 0.43], # 3 
                         [WIDTH - 1, HEIGHT * 0.48], # 4
                         [WIDTH - 1, HEIGHT * 0.83], # 5
                         [WIDTH * 0.65, HEIGHT * 0.83], # 6
                         [WIDTH * 0.60, HEIGHT * 0.55], # 7
                         [WIDTH * 0.40, HEIGHT * 0.55], # 8
                         [WIDTH * 0.35, HEIGHT * 0.83], # 9
                         [0, HEIGHT * 0.83]], dtype=np.int32) # 10
    
    ROI_mask = np.zeros_like(img)
    cv2.fillPoly(ROI_mask, [ROI_vertices], 255)
    masked_img = cv2.bitwise_and(img, ROI_mask)
    return masked_img

def average(lst):
    return int(sum(lst) / len(lst))

def sortSlopes(lines, img):
    startleftx = []
    endleftx = []
    startlefty = []
    endlefty = []
    startrightx = []
    endrightx = []
    startrighty = []
    endrighty = []
    slope = 0
    rslope = 0
    if lines is not None:
        for line in lines:
            coords = line[0]
            if (coords[2] - coords[0]) != 0:  # Avoid division by 0
                slope = (float(coords[3] - coords[1])) / \
                    (float(coords[2] - coords[0]))
                if (slope > 0.25 and slope < 0.9):
                    # cv2.line(img, (coords[0], coords[1]),
                    #          (coords[2], coords[3]), (255, 255, 255), 2)
                    startrightx.extend([coords[0]])
                    endrightx.extend([coords[2]])
                    startrighty.extend([coords[1]])
                    endrighty.extend([coords[3]])
                    # print(f"Slope Right: {slope:.3f}")
                elif (slope < -0.25 and slope > -0.9):
                    # cv2.line(img, (coords[0], coords[1]),
                    #          (coords[2], coords[3]), (255, 255, 255), 2)
                    startleftx.extend([coords[0]])
                    endleftx.extend([coords[2]])
                    startlefty.extend([coords[1]])
                    endlefty.extend([coords[3]])
        try:
            rslope = round(slope, 4)
        except:
            rslope = 0
    return startleftx, endleftx, startlefty, endlefty, startrightx, endrightx, startrighty, endrighty, rslope

def draw_lines(img, threshold, minLineLength, maxLineGap):
    lines = cv2.HoughLinesP(img, 1, np.pi/180, threshold, np.array([]), minLineLength, maxLineGap)
    # if lines is not None:
    #     for line in lines:
    #         coords = line[0]
    #         cv2.line(img, (coords[0],coords[1]), (coords[2],coords[3]),(255, 255, 255), 2)
    return lines

def process_img(image, thres1, thres2, apertureS, L2grad):
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gauss_img1 = cv2.GaussianBlur(processed_img, (3, 3), 0)
    edge_img = cv2.Canny(gauss_img1, threshold1=thres1, threshold2=thres2,apertureSize=apertureS, L2gradient=L2grad) 
    return edge_img

# # Define a function to fit a polynomial curve to lane points
# def fit_curve(x, y, degree=1):
#     coefficients = np.polyfit(x, y, degree)
#     return coefficients

# # Define a function to calculate curvature from polynomial coefficients
# def calculate_curvature(coeffs, y):
#     # Curvature formula for a polynomial curve: kappa = |2A| / (1 + (2Ax + B)^2)^(3/2)
#     A, B = coeffs[0], coeffs[1]
#     curvature = np.abs(2 * A) / (1 + (2 * A * y + B)**2)**(3/2)
#     return curvature

# def overlay_curves_on_image(img, left_coeffs, right_coeffs):
#     # Generate y values for plotting the curves (e.g., from 0 to image height)
#     y_values = np.linspace(0, img.shape[0] - 1, img.shape[0])

#     # Compute x values for the fitted curves using polynomial equations
#     left_x_values = np.polyval(left_coeffs, y_values)
#     right_x_values = np.polyval(right_coeffs, y_values)

#     # Convert float coordinates to integer for drawing
#     left_points = np.array([np.column_stack((left_x_values, y_values))], dtype=np.int32)
#     right_points = np.array([np.column_stack((right_x_values, y_values))], dtype=np.int32)

#     # Draw the fitted curves on a copy of the original image
#     img_with_curves = np.copy(img)
#     cv2.polylines(img_with_curves, left_points, isClosed=False, color=(0, 255, 0), thickness=2)
#     cv2.polylines(img_with_curves, right_points, isClosed=False, color=(255, 0, 0), thickness=2)

#     return img_with_curves

def drawLanes(startleftx, endleftx, startlefty, endlefty, startrightx, endrightx, startrighty, endrighty, img):
    lanes_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if startleftx and startlefty and endleftx and endlefty:
        # left_coeffs = fit_curve(startlefty + endlefty, startleftx + endleftx)
        # y_values = np.linspace(0, lanes_img.shape[0] - 1, lanes_img.shape[0])
        # left_curvature = calculate_curvature(left_coeffs, y_values[-1])
        # print("Left Lane Curvature:", left_curvature)

        avgStartLeftX = average(startleftx)
        avgStartLeftY = average(startlefty)
        avgEndLeftX = average(endleftx)
        avgEndLeftY = average(endlefty)
        cv2.line(lanes_img, (avgStartLeftX, avgStartLeftY), (avgEndLeftX, avgEndLeftY), (0, 255, 0), 2)

    if startrightx and startrighty and endrightx and endrighty:
        # right_coeffs = fit_curve(startrighty + endrighty, startrightx + endrightx)
        # y_values = np.linspace(0, lanes_img.shape[0] - 1, lanes_img.shape[0])
        # right_curvature = calculate_curvature(right_coeffs, y_values[-1])
        # print("Right Lane Curvature:", right_curvature)

        avgStartRightX = average(startrightx)
        avgStartRightY = average(startrighty)
        avgEndRightX = average(endrightx)
        avgEndRightY = average(endrighty)
        cv2.line(lanes_img, (avgStartRightX, avgStartRightY), (avgEndRightX, avgEndRightY), (255, 0, 0), 2)
    return lanes_img

def screen_record(data_queue):
    threshold = 125
    minLineLength = 50
    maxLineGap = 125
    thres1 = 50
    thres2 = 250
    apertureS = 3
    L2grad = True
    corners, ww, wh = get_window_corners()
    if corners:
        top_left = list(corners["top_left"])
        bottom_right = list(corners["bottom_right"])
        while True:
            printscreen = np.array(ImageGrab.grab(bbox=(top_left[0], top_left[1], bottom_right[0], bottom_right[1])))
            gauss_img = process_img(printscreen, thres1, thres2, apertureS, L2grad)
            ness_img = findRoi(gauss_img,wh,ww)
            lines = draw_lines(ness_img, threshold, minLineLength, maxLineGap)
            slx,elx,sly,ely,srx,erx,sry,ery,slope = sortSlopes(lines, ness_img)
            lanes_img1 = drawLanes(slx,elx,sly,ely,srx,erx,sry,ery,ness_img)
            data_queue.queue.clear()
            # print(f"sending slope: {slope}")
            data_queue.put(slope)
            ######################################################################################
            # try:
            #     curv_img = overlay_curves_on_image(ness_img, fit_curve(sly + ely, slx + elx), fit_curve(sry + ery, srx + erx))
            #     cv2.imshow('curv_img', curv_img)
            # except:
            #     pass
            # print(f"slope is {slope}")
            if cv2.waitKey(25) & 0xFF == ord('t'):
                threshold = int(input("Enter threshold value: "))
                minLineLength = int(input("Enter minimum line length: "))
                maxLineGap = int(input("Enter maximum line gap: "))
            cv2.imshow('window', lanes_img1)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            if cv2.waitKey(25) & 0xFF == ord('r'):
                corners = get_window_corners()
                if corners:
                    top_left = corners["top_left"]
                    bottom_right = corners["bottom_right"]
                else:
                    print("Window not found.")
    else:
        print("Window not found.")

# if __name__ == "__main__":
#     data_queue = Queue()
#     screen_record(data_queue)