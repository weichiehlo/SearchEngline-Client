# -*- mode: python -*-

block_cipher = None


a = Analysis(['SearchEngine.py'],
             pathex=['C:\\Users\\wlo\\PycharmProjects\\SearchEngine-Client'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('F.png', 'F.png', 'DATA'), ('Logo1.PNG', 'Logo1.PNG', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SearchEngine',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
