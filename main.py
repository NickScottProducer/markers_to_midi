import soundfile as sf
from pprint import pprint
import wavfile_fixed as wavfile
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage


def get_tempo_values(file):
    test = wavfile.read(file, readmarkers=True, readmarkerlabels=True, readmarkerslist=False, readloops=False,
                        readpitch=False, normalized=False, forcestereo=False)

    tempo_items = [item for item in test[4] if item.startswith(b'Tempo: ')]
    tempo_values = [float(item.decode('utf-8').split(': ')[1]) for item in tempo_items]
    return tempo_values

def get_tempo_positions(file):
    test = wavfile.read(file, readmarkers=True, readmarkerlabels=True, readmarkerslist=False, readloops=False,
                        readpitch=False, normalized=False, forcestereo=False)
    return test[3]


def create_tempo_map_midi(positions, tempos, output_midi_file='tempo_map.mid'):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    ticks_per_beat = 480  # Adjust as needed
    sample_rate = 44100  # Adjust according to the sample rate of your audio file

    # Calculate ticks per second based on the initial tempo and sample rate
    ticks_per_second = ticks_per_beat * tempos[0] / 60

    # Add tempo events to the MIDI track
    for position, tempo in zip(positions, tempos):
        microseconds_per_beat = int(60_000_000 / tempo)
        # Convert position to time in seconds
        time_seconds = position / sample_rate
        # Convert time to ticks
        time_ticks = int(time_seconds)
        # Use 'set_tempo' message for tempo changes
        track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat, time=time_ticks))

    # Set the end time of the last tempo event as the end time of the MIDI file
    end_time_ticks = int(positions[-1] / sample_rate * ticks_per_second)
    track.append(Message('note_on', note=60, velocity=64, time=end_time_ticks))
    track.append(Message('note_off', note=60, velocity=64, time=100))  # Add a short note-off event

    # Save MIDI file
    midi.save(output_midi_file)


if __name__ == "__main__":
    file_path = 'test.wav'
    tempo_values = get_tempo_values(file_path)
    pos_values = get_tempo_positions(file_path)
    create_tempo_map_midi(pos_values, tempo_values)

    print(tempo_values)
    print(pos_values)

