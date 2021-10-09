meta:
  id: hgsv_header
  title: HGSV Header
  application: Townsmen by HandyGames GmbH
  endian: le
  tags:
    - save
    - savegame
    - townsmen
  ks-version: 0.9
seq:
  - id: magic
    size: 4
    contents:
      - H # Handy
      - G # Games
      - S # Sa
      - V # Ve
    doc: HGSV magic bytes
  - id: unk_01
    type: u1
  - id: is_compressed
    type: u1
    doc: reinflate with zipstream
  - id: unk_03
    type: u2
  - id: unk_04
    type: u1
  - id: data_size
    type: u4
    doc: Size of the data section