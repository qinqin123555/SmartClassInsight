import cv2
import os

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（脚本目录的上一级）
project_root = os.path.dirname(script_dir)

# 从.avi 类型的视频中提取图像
def splitFrames(sourceFileName):

    # 在这里把后缀接上
    video_path = os.path.join(project_root, 'data', 'raw_videos', 'videos', sourceFileName + '.avi')
    # 使用绝对路径确保保存到正确的位置
    outPutDirName = os.path.join(project_root, 'data', 'processed', 'frames', sourceFileName)

    if not os.path.exists(outPutDirName):
        #如果文件目录不存在则创建目录
        os.makedirs(outPutDirName)

    cap = cv2.VideoCapture(video_path) # 打开视频文件
    num = 1
    while True:
        # success 表示是否成功，data是当前帧的图像数据；.read读取一帧图像，移动到下一帧
        success, data = cap.read()
        if not success:
            break
        # im = Image.fromarray(data, mode='RGB') # 重建图像
        # im.save('C:/Users/Taozi/Desktop/2019.04.30/' +str(num)+".jpg") # 保存当前帧的静态图像
        cv2.imwrite(os.path.join(outPutDirName, str(num) + ".jpg"), data)

        num = num + 1

        # if num % 20 == 0:
        #     cv2.imwrite('./Video_dataset/figures/' + str(num) + ".jpg", data)

        print(num)
    cap.release()

# 从.mp4 数据类型的视频中提取图像
def splitFrames_mp4(sourceFileName):

    # 在这里把后缀接上
    video_path = os.path.join(project_root, 'data', 'raw_videos', 'videos', sourceFileName + '.mp4')
    times = 0
    # 提取视频的频率，每25帧提取一个
    # frameFrequency = 25
    # 输出图片到processed/frames文件夹下
    # 使用绝对路径确保保存到正确的位置
    outPutDirName = os.path.join(project_root, 'data', 'processed', 'frames', sourceFileName)

    # 如果文件目录不存在则创建目录
    if not os.path.exists(outPutDirName):
        try:
            os.makedirs(outPutDirName)
            print(f"创建输出目录: {outPutDirName}")
        except Exception as e:
            print(f"创建目录失败: {e}")
    else:
        print(f"输出目录已存在: {outPutDirName}")

    camera = cv2.VideoCapture(video_path)
    while True:
        times+=1
        res, image = camera.read()
        if not res:
            # print('not res , not image')
            break

        # if times%frameFrequency==0:
        #     cv2.imwrite(outPutDirName + str(times)+'.jpg', image)
        #     print(outPutDirName + str(times)+'.jpg')

        frame_path = os.path.join(outPutDirName, str(times) + '.jpg')
        save_success = cv2.imwrite(frame_path, image)
        if not save_success:
            print(f"保存失败: {frame_path}")
        print(times,end='\t')
    print('\n图片提取结束')
    camera.release()

if __name__ == '__main__':

    # 打印调试信息
    print(f"脚本文件位置: {os.path.abspath(__file__)}")
    print(f"脚本目录: {script_dir}")
    print(f"项目根目录: {project_root}")

    im_file = os.path.join(project_root, 'data', 'raw_videos', 'videos')
    print(f"视频文件目录: {im_file}")

    # for im_name in im_names:
    for im_name in os.listdir(im_file):
        suffix_file = os.path.splitext(im_name)[-1]
        if suffix_file == '.mp4':
            print('~~~~~~~~~~ 从.mp4 视频提取图像 ~~~~~~~~~~~~~~~')

            sourceFileName = os.path.splitext(im_name)[0]
            splitFrames_mp4(sourceFileName)

        elif suffix_file == '.avi' :
            print('~~~~~~~~~~ 从.avi 视频提取图像 ~~~~~~~~~~~~~~~')

            sourceFileName = os.path.splitext(im_name)[0]
            splitFrames(sourceFileName)
