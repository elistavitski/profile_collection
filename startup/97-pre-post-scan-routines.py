import matplotlib.pyplot as plt
from datetime import datetime
from subprocess import call
import time
from scipy.optimize import curve_fit
from isstools.xasdata import xasdata
from bluesky.plan_stubs import mv


def write_html_log(uuid, figure, log_path='/GPFS/xf08id/User Data/'):
    # Get needed data from db
    uuid = db[uuid]['start']['uid']

    if 'name' in db[uuid]['start']:
        scan_name = db[uuid]['start']['name']
    else:
        scan_name = 'General Scan'

    year = db[uuid]['start']['year']
    cycle = db[uuid]['start']['cycle']
    proposal = db[uuid]['start']['PROPOSAL']

    # Create dirs if they are not there
    if log_path[-1] != '/':
        log_path += '/'
    log_path = '{}{}.{}.{}/'.format(log_path, year, cycle, proposal)
    if(not os.path.exists(log_path)):
        os.makedirs(log_path)
        call(['setfacl', '-m', 'g:iss-staff:rwx', log_path])
        call(['chmod', '770', log_path])

    log_path = log_path + 'log/'
    if(not os.path.exists(log_path)):
        os.makedirs(log_path)
        call(['setfacl', '-m', 'g:iss-staff:rwx', log_path])
        call(['chmod', '770', log_path])

    snapshots_path = log_path + 'snapshots/'
    if(not os.path.exists(snapshots_path)):
        os.makedirs(snapshots_path)
        call(['setfacl', '-m', 'g:iss-staff:rwx', snapshots_path])
        call(['chmod', '770', snapshots_path])

    file_path = 'snapshots/{}.png'.format(scan_name)
    fn = log_path + file_path
    repeat = 1
    while(os.path.isfile(fn)):
        repeat += 1
        file_path = 'snapshots/{}-{}.png'.format(scan_name, repeat)
        fn = log_path + file_path

    # Save figure
    figure.savefig(fn)
    call(['setfacl', '-m', 'g:iss-staff:rw', fn])
    call(['chmod', '660', fn])

    # Create or update the html file
    relative_path = './' + file_path
    
    comment = ''
    if 'comment' in db[uuid]['start']:
        comment = db[uuid]['start']['comment']
    comment = '<p><b> Comment: </b> {} </p>'.format(comment)
    start_timestamp = db[uuid]['start']['time']
    stop_timestamp = db[uuid]['stop']['time']
    time_stamp_start='<p><b> Scan start: </b> {} </p>\n'.format(datetime.fromtimestamp(start_timestamp).strftime('%m/%d/%Y    %H:%M:%S'))
    time_stamp='<p><b> Scan complete: </b> {} </p>\n'.format(datetime.fromtimestamp(stop_timestamp).strftime('%m/%d/%Y    %H:%M:%S'))
    time_total='<p><b> Total time: </b> {} </p>\n'.format(datetime.fromtimestamp(stop_timestamp - start_timestamp).strftime('%M:%S'))
    uuid_html='<p><b> Scan ID: </b> {} </p>\n'.format(uuid)

    filenames = {}
    for i in db[uuid]['descriptors']:
        if i['name'] in i['data_keys']:
            if 'filename' in i['data_keys'][i['name']]:
                name = i['name']
                if 'devname' in i['data_keys'][i['name']]:
                    name = i['data_keys'][i['name']]['devname']
                filenames[name] = i['data_keys'][i['name']]['filename']
    
    fn_html = '<p><b> Files: </b></p>\n<ul>\n'
    for key in filenames.keys():
        fn_html += '  <li><b>{}:</b> {}</ln>\n'.format(key, filenames[key])
    fn_html += '</ul>\n'
    
    image = '<img src="{}" alt="{}" height="447" width="610">\n'.format(fn, scan_name)

    if(not os.path.isfile(log_path + 'log.html')):
        create_file = open(log_path + 'log.html', "w")
        create_file.write('<html> <body>\n</body> </html>')
        create_file.close()
        call(['setfacl', '-m', 'g:iss-staff:rw', log_path + 'log.html'])
        call(['chmod', '660', log_path + 'log.html'])

    text_file = open(log_path + 'log.html', "r")
    lines = text_file.readlines()
    text_file.close()

    text_file = open(log_path + 'log.html', "w")

    for indx,line in enumerate(lines):
        if indx is 1:
            text_file.write('<header><h2> {} </h2></header>\n'.format(scan_name))
            text_file.write(comment)
            text_file.write(uuid_html)
            text_file.write(fn_html)
            text_file.write(time_stamp_start)
            text_file.write(time_stamp)
            text_file.write(time_total)
            text_file.write(image)
            text_file.write('<hr>\n\n')
        text_file.write(line)
    text_file.close()




def tune_mono_pitch(scan_range, step, retries = 1, ax = None):
    aver=pba1.adc7.averaging_points.get()
    pba1.adc7.averaging_points.put(10)
    num_points = int(round(scan_range/step) + 1)
    over = 0

    while(not over):
        RE(tune([pba1.adc7], hhm.pitch, -scan_range/2, scan_range/2, num_points, ''), LivePlot('pba1_adc7_volt', 'hhm_pitch', ax=ax))
        last_table = db.get_table(db[-1])
        min_index = np.argmin(last_table['pba1_adc7_volt'])
        hhm.pitch.move(last_table['hhm_pitch'][min_index])
        print(hhm.pitch.position)

        run = db[-1]
        os.remove(run['descriptors'][0]['data_keys'][run['descriptors'][0]['name']]['filename'])
        #for i in run['descriptors']:
        #        if 'devname' in i['data_keys'][i['name']]

        #os.remove(db[-1]['descriptors'][0]['data_keys']['pba1_adc7']['filename'])
        if (num_points >= 10):
            if (((min_index > 0.2 * num_points) and (min_index < 0.8 * num_points)) or retries == 1):
                over = 1
            if retries > 1:
                retries -= 1
        else:
            over = 1

    pba1.adc7.averaging_points.put(aver)
    print('Pitch tuning complete!')

def tune_mono_pitch_encoder(scan_range, step, retries = 1, ax = None):
    aver=pba1.adc7.averaging_points.get()
    pba1.adc7.averaging_points.put(10)
    num_points = int(round(scan_range/step) + 1)
    over = 0
	
    start_position = pb2.enc3.pos_I.value

    while(not over):
        RE(tune([pba1.adc7, pb2.enc3], hhm.pitch, -scan_range/2, scan_range/2, 2, ''))

        enc = xasdata.XASdataAbs.loadENCtrace('', '', db[-1]['descriptors'][0]['data_keys']['pb2_enc3']['filename'])
        i0 = xasdata.XASdataAbs.loadADCtrace('', '', db[-1]['descriptors'][1]['data_keys']['pba1_adc7']['filename'])
		
        min_timestamp = np.array([i0[0,0], enc[0,0]]).max()
        max_timestamp = np.array([i0[len(i0)-1,0], enc[len(enc)-1,0]]).min()
        interval = i0[1,0] - i0[0,0]
        timestamps = np.arange(min_timestamp, max_timestamp, interval)
        enc_interp = np.array([timestamps, np.interp(timestamps, enc[:,0], enc[:,1])]).transpose()
        i0_interp = np.array([timestamps, np.interp(timestamps, i0[:,0], i0[:,1])]).transpose()
        len_to_erase = int(np.round(0.015 * len(i0_interp)))
        enc_interp = enc_interp[len_to_erase:]
        i0_interp = i0_interp[len_to_erase:]
		
        xas_abs.data_manager.process_equal(i0_interp[:,0],
                                           enc_interp[:,1],
                                           i0_interp[:,1],
                                           i0_interp[:,1],
                                           i0_interp[:,1],
                                           10)
												
        xas_abs.data_manager.en_grid = xas_abs.data_manager.en_grid[5:-5]
        xas_abs.data_manager.i0_interp = xas_abs.data_manager.i0_interp[5:-5]
		#plt.plot(enc_interp[:,1], i0_interp[:,1]) #not binned
		
        plt.plot(xas_abs.data_manager.en_grid, xas_abs.data_manager.i0_interp) #binned
        minarg = np.argmin(xas_abs.data_manager.i0_interp)
        enc_diff = xas_abs.data_manager.en_grid[minarg] - start_position
		
        pitch_pos = enc_diff / 204 # Enc to pitch convertion
        print('Delta Pitch = {}'.format(pitch_pos))
		#convert enc_diff to position (need to know the relation)
		#then move to the new position
		
        print(hhm.pitch.position)
        #os.remove(db[-1]['descriptors'][0]['data_keys']['pba1_adc7']['filename'])
        over = 1

    pba1.adc7.averaging_points.put(aver)
    print('Pitch tuning complete!')


def tune_mono_y(scan_range, step, retries = 1, ax = None):
    aver=pba1.adc7.averaging_points.get()
    pba1.adc7.averaging_points.put(10)
    num_points = int(round(scan_range/step) + 1)
    over = 0

    while(not over):
        RE(tune([pba1.adc7], hhm.y, -scan_range/2, scan_range/2, num_points, ''), LivePlot('pba1_adc7_volt', 'hhm_y', ax=ax))
        last_table = db.get_table(db[-1])
        min_index = np.argmin(last_table['pba1_adc7_volt'])
        hhm.y.move(last_table['hhm_y'][min_index])
        print('New position: {}'.format(hhm.y.position))
        run = db[-1]
        os.remove(run['descriptors'][0]['data_keys'][run['descriptors'][0]['name']]['filename'])
        #os.remove(db[-1]['descriptors'][0]['data_keys']['pba1_adc7']['filename'])
        if (num_points >= 10):
            if (((min_index > 0.2 * num_points) and (min_index < 0.8 * num_points)) or retries == 1):
                over = 1
            if retries > 1:
                retries -= 1
        else:
            over = 1

    pba1.adc7.averaging_points.put(aver)
    print('Y tuning complete!')


def tune_mono_y_bpm(scan_range, step, retries = 1, ax = None):
    num_points = int(round(scan_range/step) + 1)
    over = 0

    while(not over):
        RE(tune([bpm_fm], hhm.y, -scan_range/2, scan_range/2, num_points, ''), LivePlot('bpm_fm_stats1_total', 'hhm_y', ax=ax))
        last_table = db.get_table(db[-1])
        max_index = np.argmax(last_table['bpm_fm_stats1_total'])
        hhm.y.move(last_table['hhm_y'][max_index])
        print('New position: {}'.format(hhm.y.position))
        if (num_points >= 10):
            if (((max_index > 0.2 * num_points) and (max_index < 0.8 * num_points)) or retries == 1):
                over = 1
            if retries > 1:
                retries -= 1
        else:
            over = 1

    print('Y tuning complete!')


def gauss(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))


def xia_gain_matching(center_energy, scan_range, channel_number):
    
    graph_x = xia1.mca_x.value
    graph_data = getattr(xia1, "mca_array" + "{}".format(channel_number) + ".value")

    condition = (graph_x <= (center_energy + scan_range)/1000) == (graph_x > (center_energy - scan_range)/1000)
    interval_x = np.extract(condition, graph_x)
    interval = np.extract(condition, graph_data)

    # p0 is the initial guess for fitting coefficients (A, mu and sigma)
    p0 = [.1, center_energy/1000, .1]
    coeff, var_matrix = curve_fit(gauss, interval_x, interval, p0=p0) 
    print('Intensity = ', coeff[0])
    print('Fitted mean = ', coeff[1])
    print('Sigma = ', coeff[2])

    # For testing (following two lines)
    plt.plot(interval_x, interval)
    plt.plot(interval_x, gauss(interval_x, *coeff))

    #return gauss(interval_x, *coeff)



def generate_xia_file(uuid, name, log_path='/GPFS/xf08id/Sandbox/', graph='xia1_graph3'):
    arrays = db.get_table(db[uuid])[graph]
    np.savetxt('/GPFS/xf08id/Sandbox/' + name, [np.array(x) for x in arrays], fmt='%i',delimiter=' ')


def generate_tune_table(motor=hhm.energy, start_energy=5000, stop_energy=13000, step=100):
    table = []
    for energy in range(start_energy, stop_energy + 1, step):
        motor.move(energy)
        time.sleep(0.5)
        tune_mono_pitch(2, 0.025)
        tune_mono_y(0.5, 0.01)
        table.append([energy, hhm.pitch.read()['hhm_pitch']['value'], hhm.y.read()['hhm_y']['value']])

    return table

def set_foil_reference(element = None):

    # Adding reference foil element list
    reference_foils = json.loads(open('/nsls2/xf08id/settings/json/foil_wheel.json').read())
    elems = [item['element'] for item in reference_foils]
    ##print(reference_foils[][][])

    #reference = {'Ti': {'foilwheel1': 30,  'foilwheel2': 0},
    #             'V':  {'foilwheel1': 60,  'foilwheel2': 0},
    #             'Cr': {'foilwheel1': 90,  'foilwheel2': 0},
    #             'Mn': {'foilwheel1': 120, 'foilwheel2': 0},
    #             'Fe': {'foilwheel1': 150, 'foilwheel2': 0},
    #             'Co': {'foilwheel1': 180, 'foilwheel2': 0},
    #             'Ni': {'foilwheel1': 210, 'foilwheel2': 0},
    #             'Cu': {'foilwheel1': 240, 'foilwheel2': 0},
    #             'Zn': {'foilwheel1': 270, 'foilwheel2': 0},
    #             'Pt': {'foilwheel1': 300, 'foilwheel2': 0},
    #             'Au': {'foilwheel1': 330, 'foilwheel2': 0},
    #             'Se': {'foilwheel2': 60,  'foilwheel1': 0},
    #             'Pb': {'foilwheel2': 90,  'foilwheel1': 0},
    #             'Nb': {'foilwheel2': 120, 'foilwheel1': 0},
    #             'Mo': {'foilwheel2': 150, 'foilwheel1': 0},
    #             'Ru': {'foilwheel2': 180, 'foilwheel1': 0},
    #             'Rh': {'foilwheel2': 210, 'foilwheel1': 0},
    #             'Pd': {'foilwheel2': 240, 'foilwheel1': 0},
    #             'Ag': {'foilwheel2': 270, 'foilwheel1': 0},
    #             'Sn': {'foilwheel2': 300, 'foilwheel1': 0},
    #             'Sb': {'foilwheel2': 330, 'foilwheel1': 0}
    #             }

    if element is None:
        yield from mv(foil_wheel.wheel1, 0)
        yield from mv(foil_wheel.wheel2, 0)
    else:
        if element in elems:
            indx = elems.index(element)
            yield from mv(foil_wheel.wheel2, reference_foils[indx]['fw2'])
            yield from mv(foil_wheel.wheel1, reference_foils[indx]['fw1'])
        else:
            yield from mv(foil_wheel.wheel1, 0)
            yield from mv(foil_wheel.wheel2, 0)

        #yield from mv(foil_wheel.wheel2, reference[element]['foilwheel2'])
        #yield from mv(foil_wheel.wheel1, reference[element]['foilwheel1'])

