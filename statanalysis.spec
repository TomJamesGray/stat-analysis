# -*- mode: python -*-
from kivy.tools.packaging.pyinstaller_hooks import get_deps_all

block_cipher = None


a = Analysis(['statanalysis.py'],
             pathex=['/tmp/cw_test/comp_coursework'],
             binaries=[],
             datas=[],
             hookspath=[],
             runtime_hooks=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             hiddenimports=['kivy.core',

    'kivy.core.audio',

    'kivy.core.audio.audio_avplayer',
    'kivy.core.audio.audio_ffpyplayer',
    'kivy.core.audio.audio_gstplayer',
    'kivy.core.audio.audio_pygame',

    'kivy.core.camera',

    'kivy.core.camera.camera_android',
    'kivy.core.camera.camera_gi',
    'kivy.core.camera.camera_opencv',

    'kivy.core.clipboard',

    'kivy.core.clipboard._clipboard_ext',
    'kivy.core.clipboard.clipboard_android',
    'kivy.core.clipboard.clipboard_dbusklipper',
    'kivy.core.clipboard.clipboard_dummy',
    'kivy.core.clipboard.clipboard_gtk3',
    'kivy.core.clipboard.clipboard_nspaste',
    'kivy.core.clipboard.clipboard_pygame',
    'kivy.core.clipboard.clipboard_sdl2',
    'kivy.core.clipboard.clipboard_winctypes',
    'kivy.core.clipboard.clipboard_xclip',
    'kivy.core.clipboard.clipboard_xsel',

    'kivy.core.gl',
    'kivy.core.image',

    'kivy.core.image.img_dds',
    'kivy.core.image.img_ffpyplayer',
    'kivy.core.image.img_gif',
    'kivy.core.image.img_pil',
    'kivy.core.image.img_pygame',
    'kivy.core.image.img_sdl2',
    'kivy.core.image.img_tex',

    'kivy.core.spelling',

    'kivy.core.spelling.spelling_enchant',
    'kivy.core.spelling.spelling_osxappkit',

    'kivy.core.text',

    'kivy.core.text.markup',
    'kivy.core.text.text_layout',
    'kivy.core.text.text_pil',
    'kivy.core.text.text_pygame',
    'kivy.core.text.text_sdl2',

    'kivy.core.video',

    'kivy.core.video.video_ffmpeg',
    'kivy.core.video.video_ffpyplayer',
    'kivy.core.video.video_gstplayer',
    'kivy.core.video.video_null',

    'kivy.core.window',

    'kivy.core.window.window_egl_rpi',
    'kivy.core.window.window_pygame',
    'kivy.core.window.window_sdl2',

    'kivy.graphics',

    'kivy.graphics.buffer',
    'kivy.graphics.cgl',
    'kivy.graphics.cgl_backend',

    'kivy.graphics.cgl_backend.cgl_debug',
    'kivy.graphics.cgl_backend.cgl_gl',
    'kivy.graphics.cgl_backend.cgl_glew',
    'kivy.graphics.cgl_backend.cgl_mock',
    'kivy.graphics.cgl_backend.cgl_sdl2',

    'kivy.graphics.compiler',
    'kivy.graphics.context',
    'kivy.graphics.context_instructions',
    'kivy.graphics.fbo',
    'kivy.graphics.gl_instructions',
    'kivy.graphics.instructions',
    'kivy.graphics.opengl',
    'kivy.graphics.opengl_utils',
    'kivy.graphics.scissor_instructions',
    'kivy.graphics.shader',
    'kivy.graphics.stencil_instructions',
    'kivy.graphics.svg',
    'kivy.graphics.tesselator',
    'kivy.graphics.texture',
    'kivy.graphics.transformation',
    'kivy.graphics.vbo',
    'kivy.graphics.vertex',
    'kivy.graphics.vertex_instructions',

    'xml.etree.cElementTree',
    'scipy._lib.messagestream',
    'sklearn.neighbors.typedefs'])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='statanalysis',
          debug=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas + [("stat_analysis/stat.kv","/tmp/cw_test/comp_coursework/stat_analysis/stat.kv","DATA")],
               Tree('res',prefix='res'),
               strip=False,
               upx=True,
               name='statanalysis')
