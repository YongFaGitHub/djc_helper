import os
import re
import shutil
import subprocess
from datetime import datetime

# ---------------准备工作
version = input("请输入版本号：")

version_reg = r"\d+\.\d+\.\d+"

if re.match(version_reg, version) is None:
    print("版本号格式有误，正确的格式类似：1.0.0 ，而不是 {}".format(version))
    exit(-1)

version = 'v' + version

run_start_time = datetime.now()
print("开始发布版本 {}".format(version))

# 先声明一些需要用到的目录的地址
dir_src = os.path.realpath('.')
dir_all_release = os.path.realpath(os.path.join("releases"))
release_dir_name = "道聚城自动化助手_{version}_by风之凌殇".format(version=version)
dir_current_release = os.path.realpath(os.path.join(dir_all_release, release_dir_name))
path_bz = os.path.join(dir_src, "bandizip_portable", "bz.exe")

# ---------------复制文件到目标目录
os.chdir(dir_src)

# 需要复制的文件与目录
files_to_copy = []
reg_wantted_file = r'.*\.(py|toml|md|bat|txt|png|ico|docx|html)$'
for file in os.listdir('.'):
    if not re.search(reg_wantted_file, file, flags=re.IGNORECASE):
        continue
    files_to_copy.append(file)
files_to_copy.extend([
    "bandizip_portable",
    "reference_data",
    "chrome_portable_85.0.4183.59.7z",
    "chromedriver_85.0.4183.87.exe",
    "public_key.der",
])
files_to_copy = sorted(files_to_copy)

# 确保发布根目录存在
if not os.path.isdir(dir_all_release):
    os.mkdir(dir_all_release)
# 并清空当前的发布版本目录
shutil.rmtree(dir_current_release, ignore_errors=True)
os.mkdir(dir_current_release)
# 复制文件与目录过去
print("将以下内容从{}复制到{}".format(dir_src, dir_current_release))
for filename in files_to_copy:
    source = os.path.join(dir_src, filename)
    destination = os.path.join(dir_current_release, filename)
    if os.path.isdir(filename):
        print("拷贝目录 {}".format(filename))
        shutil.copytree(source, destination)
    else:
        print("拷贝文件 {}".format(filename))
        shutil.copyfile(source, destination)

# ---------------构建
# 调用构建脚本
os.chdir(dir_current_release)
subprocess.call(["python", "_build.py"])

# 压缩打包
os.chdir(dir_all_release)
print("开始压缩打包")
release_7z_name = '{}.7z'.format(release_dir_name)
subprocess.call([path_bz, 'c', '-y', '-r', '-aoa', '-fmt:7z', '-l:9', release_7z_name, release_dir_name])

# ---------------推送版本到github
# 打包完成后git添加标签
os.chdir(dir_src)
print("开始推送到github")
# 先尝试移除该tag，并同步到github，避免后面加标签失败
subprocess.call(['git', 'tag', '-d', version])
subprocess.call(['git', 'push', 'origin', 'master', ':refs/tags/{version}'.format(version=version)])
# 然后添加新tab，并同步到github
subprocess.call(['git', 'tag', '-a', version, '-m', 'release {version}'.format(version=version)])
subprocess.call(['git', 'push', 'origin', 'master', '--tags'])

# ---------------结束
print('+' * 40)
print("发布完成，请将压缩包合适命名后上传至蓝奏云")
print('+' * 40)

os.system("PAUSE")
