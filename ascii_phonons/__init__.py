import os
from subprocess import call
import tempfile

ascii_phonons_path = os.path.abspath(os.path.join(
     os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
addons_path = os.path.join(ascii_phonons_path, 'addons')

def call_blender(input_file, blender_bin=False, mode_index=0, supercell=(2,2,2),
         animate=True, n_frames=30, bbox=True, bbox_offset=(0,0,0),
         vectors=False, output_file=False, vib_magnitude=1.0, arrow_magnitude=1.0,
         gui=False, gif=False, scale_factor=1.0, camera_rot=0., user_config=False):
    input_file = os.path.abspath(input_file)
    if output_file:
        output_file = os.path.abspath(output_file)
    handle, python_tmp_file = tempfile.mkstemp(suffix='.py', dir='.')

    if blender_bin:
        call_args = [blender_bin]
    else:
        import platform
        if platform.mac_ver()[0] != '':
            #call_args = ['open','-a','blender','--args']
            call_args=['/Applications/Blender/blender.app/Contents/MacOS/blender']
        else:
            call_args = ['blender']

    if not animate:
        n_frames=1

    if gif and output_file:
        gif_name = output_file + '.gif'
        handle, image_tmp_filename = tempfile.mkstemp(dir='.')
        output_file = image_tmp_filename
        os.remove(image_tmp_filename) # We only needed the name
    
    python_txt = """
import sys
from os.path import pathsep

sys.path = ['{add_path}'] + sys.path

import bpy
import vsim2blender
import vsim2blender.plotter

config = vsim2blender.read_config(user_config={config})

vsim2blender.plotter.open_mode('{0}', {1}, animate={2}, n_frames={3},
                                vectors={4}, scale_factor={5}, vib_magnitude={6},
                                arrow_magnitude={7}, supercell=({8},{9},{10}),
                                bbox={11}, bbox_offset={12}, camera_rot={13},
                                config=config)
vsim2blender.plotter.setup_render(n_frames={3})
vsim2blender.plotter.render(output_file='{out_file}')
""".format(input_file, mode_index, animate, n_frames, vectors,
           scale_factor, vib_magnitude, arrow_magnitude,
           supercell[0], supercell[1], supercell[2], bbox, bbox_offset, camera_rot,
           out_file=output_file, add_path=addons_path,
           config=user_config)

    with open(python_tmp_file, 'w') as f:
        f.write(python_txt)

    if output_file and not gui:
        call_args.append("--background")

    call_args = call_args + ["-P", python_tmp_file]

    call(call_args)

    os.remove(python_tmp_file)

    if gif and output_file:
        tmp_files = [image_tmp_filename + '{0:04.0f}'.format(i) + '.png' for i in range(n_frames)]
        convert_call_args = ['convert', '-delay', '10'] + tmp_files + ['-loop', '0', gif_name]
        try:
            call(convert_call_args)
        except:
            pass
        for f in tmp_files:
            os.remove(f)
        