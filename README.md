## 환경 세팅
<img width="824" height="434" alt="Image" src="https://github.com/user-attachments/assets/27c0e338-3fe3-4867-a7bd-9618171fe002" />
<img width="322" height="362" alt="Image" src="https://github.com/user-attachments/assets/aa6596ef-266f-47a7-9488-b0c515ee4c3e" />


## 호모그래피 과정

1. 맵의 기준점들의 월드 좌표를 world_point.csv 파일로 저장한다. csvread.py로 그 좌표들을 읽어볼 수 있다.

   
2. 각 카메라의 보정된 사진들을 따로 저장[ex)test16.jpg]하고, collectpix폴더의 collect_point_click_cam1~4.py를 실행하며 각 기준점들의 픽셀 좌표를 수동으로 찍는다.


   그렇게 하면 cam1~4_pix.csv 파일로 기준점들의 픽셀 좌표들이 저장이 된다.


3. estimate_H 폴더에서 estimate_H cam1~4.py를 실행한다. world_point.csv의 월드 좌표와 cam1~4_pix.csv 픽셀 좌표간 대응을 이용하여 호모그래피 행렬 H를 구하게 된다.


   H는 넘파이 행렬이며, H_cam1~4.npy 형식으로 저장이 된다. 이때 RMSE 값도 함께 검출이 된다.


### 테스트

readH.py로 임의의 픽셀 좌표(1234.5, 845.2)를 위 과정을 통해서 구한 H행렬을 이용하여, 월드좌표로 변환한다. 


<img width="608" height="142" alt="image" src="https://github.com/user-attachments/assets/2e69ab78-df17-4eff-83f2-f77a578469d2" />
