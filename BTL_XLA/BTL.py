import cv2
import numpy as np
import math

# ĐỌC ẢNH
img = cv2.imread("anh2.jpg")
if img is None:
    print("Khong tim thay anh!")
    exit()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(5,5),0)

_,thresh = cv2.threshold(blur,150,255,cv2.THRESH_BINARY_INV)

kernel = np.ones((3,3),np.uint8)
thresh = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel)

contours,_ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

result = img.copy()

# BỘ ĐẾM
triangle=square=rectangle=rhombus=0
trapezoid=parallelogram=0
circle=heart=star=hexagon=0
pentagon=heptagon=nonagon=0

# HÀM TÍNH GÓC
def angle(pt1,pt2,pt3):
    v1 = pt1-pt2
    v2 = pt3-pt2
    cos = np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))
    cos = np.clip(cos,-1,1)
    return np.degrees(np.arccos(cos))

# HÀM TÍNH HỆ SỐ GÓC
def slope(p1,p2):
    if p2[0]-p1[0]==0:
        return 999
    return (p2[1]-p1[1])/(p2[0]-p1[0])

# NHẬN DẠNG
for cnt in contours:

    area = cv2.contourArea(cnt)
    if area < 1500:
        continue

    peri = cv2.arcLength(cnt,True)
    approx = cv2.approxPolyDP(cnt,0.01*peri,True)
    vertices = len(approx)

    x,y,w,h = cv2.boundingRect(cnt)
    shape="Khac"

    circularity = 4*np.pi*area/(peri*peri)

    # HÌNH TRÒN
    if circularity > 0.87 and vertices > 12 and cv2.isContourConvex(approx):
        shape="Hinh tron"
        circle+=1

    # TAM GIAC
    elif vertices==3:
        shape="Tam giac"
        triangle+=1

    # LUC GIAC
    elif vertices==6:
        shape="Luc giac"
        hexagon+=1

    # NGU GIAC

    elif vertices==5 and cv2.isContourConvex(approx):
        shape="Ngu giac"
        pentagon+=1

    # THAT GIAC
    elif vertices==7 and cv2.isContourConvex(approx):
        shape="That giac"
        heptagon+=1

    # CUU GIAC
    elif vertices==9 and cv2.isContourConvex(approx):
        shape="Cuu giac"
        nonagon+=1

    # SHAPE LÕM (Tim / Sao / Mui ten / Tia set)
    elif not cv2.isContourConvex(approx):

        hull = cv2.convexHull(cnt, returnPoints=False)
        defects = cv2.convexityDefects(cnt, hull)

        defect_count = 0
        if defects is not None:
            for i in range(defects.shape[0]):
                s,e,f,d = defects[i,0]
                if d > 2000:
                    defect_count += 1

        ratio = w/float(h)

        # ⭐ Ngôi sao (nhiều lõm sâu)
        if defect_count >= 4:
            shape="Ngoi sao"
            star+=1

        # ❤️ Trái tim (1 lõm lớn ở đỉnh)
        elif defect_count == 1:
            shape="Trai tim"
            heart+=1

        # ➡ Mũi tên (2 lõm + dài ngang)
        elif defect_count == 2 and ratio > 1.2:
            shape="Mui ten"

        # ⚡ Tia sét (3 lõm trở lên nhưng không đối xứng)
        elif defect_count >= 2 and ratio < 1.2:
            shape="Tia set"

        else:
            shape="Khac"

    # TỨ GIÁC
    elif vertices==4:

        pts = approx.reshape(4,2)

        d = [np.linalg.norm(pts[i]-pts[(i+1)%4]) for i in range(4)]
        ang = [angle(pts[i-1],pts[i],pts[(i+1)%4]) for i in range(4)]
        right = all(80<a<100 for a in ang)

        s1 = slope(pts[0],pts[1])
        s2 = slope(pts[2],pts[3])
        s3 = slope(pts[1],pts[2])
        s4 = slope(pts[3],pts[0])

        parallel1 = abs(s1-s2)<0.2
        parallel2 = abs(s3-s4)<0.2

        # Vuong
        if right and max(d)-min(d)<20:
            shape="Hinh vuong"
            square+=1

        # Chu nhat
        elif right:
            shape="Hinh chu nhat"
            rectangle+=1

        # Thoi
        elif max(d)-min(d)<20:
            shape="Hinh thoi"
            rhombus+=1

        # Binh hanh
        elif parallel1 and parallel2:
            shape="Hinh binh hanh"
            parallelogram+=1

        # Hinh thang
        elif parallel1 or parallel2:
            shape="Hinh thang"
            trapezoid+=1

        else:
            shape="Tu giac khac"

    # ĐA GIÁC 8-10 CẠNH
    elif vertices==8:
        shape="Bat giac"
    elif vertices==10:
        shape="Thap giac"

    cv2.drawContours(result,[cnt],-1,(0,255,0),2)
    cv2.putText(result,shape,(x,y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,(0,0,255),2)

# KẾT QUẢ
print("Tam giac:",triangle)
print("Hinh vuong:",square)
print("Hinh chu nhat:",rectangle)
print("Hinh thoi:",rhombus)
print("Hinh binh hanh:",parallelogram)
print("Hinh thang:",trapezoid)
print("Hinh tron:",circle)
print("Luc giac:",hexagon)
print("Ngu giac:",pentagon)
print("That giac:",heptagon)
print("Cuu giac:",nonagon)
print("Ngoi sao:",star)
print("Trai tim:",heart)

cv2.imshow("Ket qua",result)
cv2.waitKey(0)
cv2.destroyAllWindows()
