libdir = get_option('libdir')

# Prefer newest ABI first
budgie_pc_names = [
  'budgie-3.0',
  'budgie-2.0',
  'budgie-1.0',
]

budgie_dep = dependency(
  budgie_pc_names,
  required: true
)

message('Using Budgie ABI: ' + budgie_dep.name())

budgie_plugin_dir = libdir / 'budgie-desktop' / 'plugins' / 'budgiesysmonitor'

install_data(
  'budgiesysmonitor.py',
  install_dir: budgie_plugin_dir,
  install_mode: 'rwxr-xr-x'
)

budgie_2 = get_option('for-wayland')

plugininstall = configure_file(
    input: 'BudgieSysMonitor.plugin.in',
    output: 'BudgieSysMonitor.plugin',
    configuration: {'PYTHON': budgie_2 ? 'python' : 'python3' }
)

install_data(
  plugininstall,
  install_dir: budgie_plugin_dir
)
