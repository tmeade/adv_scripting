import os, subprocess, shutil

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

def main():
    print('RUN TESTS')
    mayapy = '/Applications/Autodesk/maya2023/Maya.app/Contents/bin/mayapy'
    mayaunittest = f'{ROOT_DIR}/adv_scripting/tests.py'
    cmd = [mayapy, mayaunittest]
    if not os.path.exists(cmd[0]):
        raise RuntimeError('Maya {0} is not installed on this system.'.format(mayapy))

    try:
        subprocess.run(cmd)
    except subprocess.CalledProcessError:
        print(subprocess.CalledProcessError.stderr)
        print(subprocess.CalledProcessError.stdout)


if __name__ == '__main__':
    main()
