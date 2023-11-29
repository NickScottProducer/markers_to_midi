import warnings
from pprint import pprint
import wavfile_fixed as wavfile
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage


warnings.filterwarnings("ignore", message="Chunk b'JUNK' skipped", category=UserWarning)
warnings.filterwarnings("ignore", message="Chunk b'LGWV' skipped", category=UserWarning)
warnings.filterwarnings("ignore", message="Chunk b'ResU' skipped", category=UserWarning)
warnings.filterwarnings("ignore", message="Chunk b'bext' skipped", category=UserWarning)


def get_tempo_values(file):
    test = wavfile.read(file, readmarkers=True, readmarkerlabels=True, readmarkerslist=False, readloops=False,
                        readpitch=False, normalized=False, forcestereo=False)
    tempo_items = [item for item in test[4] if item.startswith(b'Tempo: ')]
    tempo_values = [float(item.decode('utf-8').split(': ')[1]) for item in tempo_items]

    return tempo_values


def get_tempo_positions(file):
    test = wavfile.read(file, readmarkers=True, readmarkerlabels=True, readmarkerslist=False, readloops=False,
                        readpitch=False, normalized=False, forcestereo=False)

    # Filter positions to include only tempo markers
    tempo_positions = [pos for pos, marker in zip(test[3], test[4]) if marker.startswith(b'Tempo: ')]

    return tempo_positions


def create_tempo_map_midi(positions, tempos, sample_rate=44100, output_midi_file='tempo_map.mid'):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)
    ticks_per_beat = 480

    current_ticks = 0  # Track the cumulative ticks

    for position, tempo in zip(positions, tempos):
        bpm_to_microseconds = mido.bpm2tempo(tempo)
        time_seconds = position / sample_rate
        time_ticks = int(mido.second2tick(time_seconds, ticks_per_beat, bpm_to_microseconds))
        # Ensure that the calculated time_ticks is non-negative
        delta_ticks = max(0, time_ticks - current_ticks)
        #delta_ticks = tempo * time_ticks / ticks_per_beat
        # Add the tempo change event to the track
        track.append(MetaMessage('set_tempo', tempo=(int(bpm_to_microseconds)), time=delta_ticks))


        # Update current_ticks
        current_ticks = time_ticks

    # Save the MIDI file
    midi.save('tempo_changes.mid')


if __name__ == "__main__":
    file_path = 'test.wav'
    tempo_values = get_tempo_values(file_path)
    pos_values = get_tempo_positions(file_path)
    create_tempo_map_midi(pos_values, tempo_values)
    #print (tempo_values)
    #print (pos_values)
