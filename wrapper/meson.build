project('pyautosplit-wrapper', 'c')

executable(
    'pyautosplit-wrapper',
    'pyautosplit-wrapper.c',
    dependencies: [
        dependency('python3-embed'),
    ],
    c_args: '-DSCRIPT="' + get_option('pyautosplit') + '"',
    install: true,
)
