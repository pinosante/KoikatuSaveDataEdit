#!/usr/bin/env python
import argparse
import struct
import io
import pprint
import msgpack

class KoikatuCharacter:
    def __init__(self, data, with_card=True, skip_additional=False):
        self.with_card = with_card
        if with_card:
            # read first PNG
            self.card_png = self._read_png(data)

        #  header
        self.product_no = self._read_int(data)
        self.marker = self._read_utf8_string(data)

        # version?
        self.unknown01 = self._read_utf8_string(data)

        # second PNG
        self.png_length = self._read_int(data)
        self.png = self._read_png(data)

        # list info
        self.list_info_size = self._read_int(data)
        self.list_info_data = data.read(self.list_info_size)
        self.list_info = msgpack.unpackb(self.list_info_data,
                                         encoding='utf8')
        #print('listinfo:', self.list_info)

        # character info
        self.chara_datasize = struct.unpack("q", data.read(8))[0]
        self.chara_data = data.read(self.chara_datasize)
        self.character_info = {}
        for info in self.list_info['lstInfo']:
            start = info['pos']
            end = info['pos'] + info['size']
            part = self.chara_data[start:end]
            if info['name'] == 'Custom':
                self._read_custom(part)
            elif info['name'] == 'Coordinate':
                self._read_coordinate(part)
            elif info['name'] == 'Parameter':
                self._read_parameter(part)
            elif info['name'] == 'Status':
                self._read_status(part)
            else:
                raise ValueError(f'Unsupported info {info["name"]}')

        #print('name:', self.firstname, self.lastname)

        self.additional_keys = []
        self.additional = {}
        self.ac = {}
        self.ex_data = b''
        if not with_card:
            # additional info
            len1 = self._read_byte(data)
            if len1 == 4:
                marker = data.read(len1)
                if marker == b'KKEx':
                    # bepinex extensible format
                    version = self._read_int(data)
                    len2 = self._read_int(data)
                    ex_data = data.read(len2)
                    self.ex_data = b''.join([
                        self._pack_byte(len1),
                        marker,
                        self._pack_int(version),
                        self._pack_int(len2),
                        ex_data
                    ])
            else:
                data.seek(-1, 1)

            self.unknown02 = data.read(4)
            self.unknown_mark = data.read(4)

            self.dearname = self._read_utf8_string(data)
            #print('dear:', self.dearname)

            self.feeling = self._read_int(data)
            self.m_love = self._read_int(data)
            self.h_count = self._read_int(data)
            self.koikatu = self._read_byte(data)
            self.lover = self._read_byte(data)
            self.anger = self._read_byte(data)

            #print('feeling', self.feeling)
            #print('m_love', self.m_love)
            #print('h_count', self.h_count)
            #print('lover:', self.lover)

            #print('h_count:', self.h_count)
            #print('koikatu:', self.koikatu)
            #print('sex:', self.sex)
            #if self.koikatu > 1:
            #    self.koikatu = 0

            self.unknown03 = data.read(1)
            self.unknown04 = data.read(4)

            self.date = self._read_byte(data)
            self.unknown05 = data.read(3)

            #print('date:', self.date)
            #if self.date > 1:
            #    self.date = 0

            if not skip_additional:
                self.unknown06 = data.read(18)

                self.ac['mune'] = data.read(4)
                self.ac['kokan'] = data.read(4)
                self.ac['anal'] = data.read(4)
                self.ac['siri'] = data.read(4)
                self.ac['tikubi'] = data.read(4)

                self.unknown07 = data.read(14)

                self.ac['kokan_piston'] = data.read(4)
                self.ac['anal_piston'] = data.read(4)
            else:
                self.unknown06 = b''
                self.ac['mune'] = b''
                self.ac['kokan'] = b''
                self.ac['anal'] = b''
                self.ac['siri'] = b''
                self.ac['tikubi'] = b''
                self.unknown07 = b''
                self.ac['kokan_piston'] = b''
                self.ac['anal_piston'] = b''

            self._read_additional(data)


    @property
    def firstname(self):
        return self.parameter['firstname']

    @firstname.setter
    def firstname(self, value):
        self.parameter['firstname'] = value

    @property
    def lastname(self):
        return self.parameter['lastname']

    @lastname.setter
    def lastname(self, value):
        self.parameter['lastname'] = value

    @property
    def nickname(self):
        return self.parameter['nickname']

    @nickname.setter
    def nickname(self, value):
        self.parameter['nickname'] = value

    @property
    def sex(self):
        return self.parameter['sex']

    @sex.setter
    def sex(self, value):
        self.parameter['sex'] = value

    @property
    def answers(self):
        return self.parameter['awnser']

    @answers.setter
    def answers(self, value):
        self.parameter['awnser'] = value

    @property
    def denials(self):
        return self.parameter['denial']

    @denials.setter
    def denials(self, value):
        self.parameter['denial'] = value

    @property
    def attributes(self):
        return self.parameter['attribute']

    @attributes.setter
    def attributes(self, value):
        self.parameter['attribute'] = value

    @property
    def personality(self):
        return self.parameter['personality']

    @personality.setter
    def personality(self, value):
        self.parameter['personality'] = value

    @property
    def weak_point(self):
        return self.parameter['weakPoint']

    @weak_point.setter
    def weak_point(self, value):
        self.parameter['weakPoint'] = value

    @property
    def custom(self):
        return (self.face, self.body, self.hair)

    @custom.setter
    def custom(self, value):
        self.face = value[0]
        self.body = value[1]
        self.hair = value[2]

    def get_ac(self, key):
        return 1 if self.ac[key] == b'\x00\x00\xc8\x42' else 0

    def set_ac(self, key, value):
        if len(self.ac[key]) > 0:
            self.ac[key] = b'\x00\x00\xc8\x42' if value else b'\x00\x00\x00\x00'


    def save(self, out):
        out.write(self._serialize())

    def _serialize(self):
        custom_s = self._pack_custom()
        coordinate_s = self._pack_coordinate()
        parameter_s = self._pack_parameter()
        status_s = self._pack_status()
        chara_values = b"".join([
            custom_s,
            coordinate_s,
            parameter_s,
            status_s
        ])

        pos = 0
        for i, n in enumerate(self.list_info["lstInfo"]):
            if n["name"] == "Custom":
                self.list_info["lstInfo"][i]["pos"] = pos
                self.list_info["lstInfo"][i]["size"] = len(custom_s)
                pos += len(custom_s)
            elif n["name"] == "Coordinate":
                self.list_info["lstInfo"][i]["pos"] = pos
                self.list_info["lstInfo"][i]["size"] = len(coordinate_s)
                pos += len(coordinate_s)
            elif n["name"] == "Parameter":
                self.list_info["lstInfo"][i]["pos"] = pos
                self.list_info["lstInfo"][i]["size"] = len(parameter_s)
                pos += len(parameter_s)
            elif n["name"] == "Status":
                self.list_info["lstInfo"][i]["pos"] = pos
                self.list_info["lstInfo"][i]["size"] = len(status_s)
                pos += len(status_s)
        list_info_s = msgpack.packb(self.list_info, use_single_float=True, use_bin_type=True)

        data = []
        if self.with_card:
            data = [self.card_png]

        data += [
            self._pack_int(self.product_no),
            self._pack_utf8_string(self.marker),
            self._pack_utf8_string(self.unknown01),
            self._pack_int(self.png_length),
            self.png,
            self._pack_int(len(list_info_s)),
            list_info_s,
            struct.pack('q', len(chara_values)),
            chara_values,
            self.ex_data,
            self.unknown02,
            self.unknown_mark,
            self._pack_utf8_string(self.dearname),
            self._pack_int(self.feeling),
            self._pack_int(self.m_love),
            self._pack_int(self.h_count),
            self._pack_byte(self.koikatu),
            self._pack_byte(self.lover),
            self._pack_byte(self.anger),
            self.unknown03,
            self.unknown04,
            self._pack_byte(self.date),
            self.unknown05,
            self.unknown06,
            self.ac['mune'],
            self.ac['kokan'],
            self.ac['anal'],
            self.ac['siri'],
            self.ac['tikubi'],
            self.unknown07,
            self.ac['kokan_piston'],
            self.ac['anal_piston'],
            self._pack_additional()
        ]

        return b''.join(data)


    def _pack_chardata(self):
        return self.chara_data


    def _read_custom(self, data):
        data_stream = io.BytesIO(data)
        length = self._read_int(data_stream)
        self.face = msgpack.unpackb(data_stream.read(length), encoding='ascii')
        length = self._read_int(data_stream)
        self.body = msgpack.unpackb(data_stream.read(length), encoding='ascii')
        length = self._read_int(data_stream)
        self.hair = msgpack.unpackb(data_stream.read(length), encoding='ascii')


    def _pack_custom(self):
        face_s = msgpack.packb(self.face, use_single_float=True, use_bin_type=True)
        body_s = msgpack.packb(self.body, use_single_float=True, use_bin_type=True)
        hair_s = msgpack.packb(self.hair, use_single_float=True, use_bin_type=True)
        data = [
            struct.pack("i", len(face_s)),
            face_s,
            struct.pack("i", len(body_s)),
            body_s,
            struct.pack("i", len(hair_s)),
            hair_s
        ]
        return b"".join(data)


    def _read_coordinate(self, data):
        self.coordinates = []
        for coordinate_data in msgpack.unpackb(data):
            coordinate = {}
            data_stream = io.BytesIO(coordinate_data)
            length = self._read_int(data_stream)
            coordinate["clothes"] = msgpack.unpackb(data_stream.read(length), encoding='ascii')
            length = self._read_int(data_stream)
            coordinate["accessory"] = msgpack.unpackb(data_stream.read(length), encoding='ascii')
            makeup = self._read_byte(data_stream)
            coordinate["enableMakeup"] = True if makeup != 0 else False
            length = self._read_int(data_stream)
            coordinate["makeup"] = msgpack.unpackb(data_stream.read(length), encoding='ascii')
            self.coordinates.append(coordinate)


    def _pack_coordinate(self):
        data = []
        for i in self.coordinates:
            cloth_s = msgpack.packb(i["clothes"], use_single_float=True, use_bin_type=True)
            accessory_s = msgpack.packb(i["accessory"], use_single_float=True, use_bin_type=True)
            makeup_s = msgpack.packb(i["makeup"], use_single_float=True, use_bin_type=True, strict_types=True)
            coordinate = [
                struct.pack("i", len(cloth_s)),
                cloth_s,
                struct.pack("i", len(accessory_s)),
                accessory_s,
                struct.pack("b", 1) if i["enableMakeup"] else struct.pack("b", 0),
                struct.pack("i", len(makeup_s)),
                makeup_s
            ]
            data.append(b"".join(coordinate))
        return msgpack.packb(data, use_bin_type=True)


    def _read_parameter(self, data):
        self.parameter = msgpack.unpackb(data, encoding='utf8')


    def _pack_parameter(self):
        return msgpack.packb(self.parameter, use_single_float=True, use_bin_type=True)


    def _read_status(self, data):
        self.status = msgpack.unpackb(data, encoding='utf8')


    def _pack_status(self):
        return msgpack.packb(self.status, use_single_float=True, use_bin_type=True)


    def _read_additional(self, data):
        chunk = data.read()

        start = chunk.find(b'Idle')
        if start == -1:
            self.before_additional = chunk
            self.ac['houshi'] = b''
            self.after_additional = b''
            return

        # -1 is length byte of 'Idle'
        self.before_additional = chunk[0:start-1]

        stream = io.BytesIO(chunk[start + len('Idle'):])
        value = self._read_int(stream)

        self.additional_keys.append('Idle')
        self.additional['Idle'] = value

        while True:
            len_ = self._read_byte(stream)
            if len_ == 0:
                stream.seek(-1, 1)
                break
            key = stream.read(len_).decode('ascii')
            value = self._read_int(stream)

            self.additional_keys.append(key)
            self.additional[key] = value

        self.ac['houshi'] = stream.read(4)
        self.after_additional = stream.read()


    def _pack_additional(self):
        data = [self.before_additional]

        for key in self.additional_keys:
            data.append(self._pack_byte(len(key)))
            data.append(key.encode())
            data.append(self._pack_int(self.additional[key]))

        data.append(self.ac['houshi'])
        data.append(self.after_additional)
        return b''.join(data)


    def _read_utf8_string(self, data):
        len_ = self._read_byte(data)
        value = data.read(len_)
        return (value.decode('utf8'), len_)


    def _pack_utf8_string(self, string):
        len_ = self._pack_byte(string[1])
        binary = string[0].encode()
        return len_ + binary


    def _read_byte(self, data):
        return struct.unpack('b', data.read(1))[0]


    def _pack_byte(self, size):
        return struct.pack('b', size)


    def _read_int(self, data, endian='<'):
        return struct.unpack(endian + 'i', data.read(4))[0]


    def _pack_int(self, size, endian='<'):
        return struct.pack(endian + 'i', size)


    def _read_png(self, data):
        signature = data.read(8) # PNG file signature
        assert signature == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'

        ihdr = data.read(25)

        # read IDAT chunk
        idat_chunks = []
        len_ = self._read_int(data, '!')
        while len_ > 0:
            idat_type = data.read(4)
            assert idat_type == b'IDAT'

            idat_data = data.read(len_)
            idat_crc = data.read(4)
            idat_chunks.append((len_, idat_type, idat_data, idat_crc))

            len_ = self._read_int(data, '!')

        # read IEND chunk
        iend_len = len_
        iend = data.read(4)
        assert iend == b'IEND'

        iend_crc = data.read(4)

        data = [signature, ihdr]
        for idat_chunk in idat_chunks:
            data += [
                self._pack_int(idat_chunk[0], '!'),
                idat_chunk[1], idat_chunk[2], idat_chunk[3]
            ]
        data += [self._pack_int(iend_len, '!'), iend, iend_crc]

        return b"".join(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('png_file')

    args = parser.parse_args()

    with open(args.png_file, 'rb') as infile:
        chara = KoikatuCharacter(infile, True)

        pprint.pprint(chara.parameter)
        #pprint.pprint(chara.status)
        #pprint.pprint(chara.additional)

