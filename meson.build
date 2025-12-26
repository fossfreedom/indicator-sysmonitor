project(
  'indicator-sysmonitor',
  version: '0.11.0',
  meson_version: '>= 0.59'
)

python = import('python').find_installation()

subdir('sysmonitor_common')
subdir('indicator_sysmonitor')
subdir('data')
#subdir('icons')

if get_option('budgie')
  subdir('budgie')
endif
