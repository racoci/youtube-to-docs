import json
import numpy as np
import colorsys
import glob
from odf.opendocument import OpenDocumentText
from odf.text import P, Span
from odf.style import Style, TextProperties, PageLayout, PageLayoutProperties, MasterPage


# Function to calculate duodeciles
def calculate_duodeciles(durations):
    percentiles = np.linspace(8.33, 100, 12)
    duodeciles = np.percentile(durations, percentiles).tolist()
    return duodeciles


# Function to interpolate color based on duration and probability
def interpolate_color(duration, probability, duodeciles):
    position = np.searchsorted(duodeciles, duration) / len(duodeciles)
    hue = probability/3
    saturation = 1
    value = 2/3 + position/3
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))


# Process each JSON file
for file_name in glob.glob('*transcription.json'):
    with open(file_name, 'r', encoding='utf-8') as file:
        transcription_data = json.load(file)

    # Create a new ODT document
    doc = OpenDocumentText()

    # Define a page layout with a dark grey background
    page_layout = PageLayout(name="MyPageLayout")
    page_layout_properties = PageLayoutProperties(backgroundcolor="#000000")  # Dark grey color
    page_layout.addElement(page_layout_properties)
    doc.automaticstyles.addElement(page_layout)

    # Create a master page that uses the page layout
    master_page = MasterPage(name="Standard", pagelayoutname=page_layout)
    doc.masterstyles.addElement(master_page)
    durations = [word['end'] - word['start'] for segment in transcription_data['segments'] for word in segment['words']]
    duodeciles = calculate_duodeciles(durations)

    for segment in transcription_data['segments']:
        segment_paragraph = P()  # Create a paragraph for the segment
        for word_info in segment['words']:
            color = interpolate_color(word_info['end'] - word_info['start'], word_info['probability'], duodeciles)
            word_style = Style(name="WordStyle" + str(word_info['start']), family="text")
            word_style.addElement(TextProperties(attributes={'color': color}))
            doc.styles.addElement(word_style)

            # Create a Span element for the word with the style
            word_span = Span(text=word_info['word'] + ' ', stylename=word_style)
            segment_paragraph.addElement(word_span)
        doc.text.addElement(segment_paragraph)  # Add the segment paragraph to the document

    odt_file_name = file_name.replace('.json', '.odt')
    doc.save(odt_file_name)
