from zebv.interact import Interaction

data = """
statefuldraw = ap ap b ap b ap ap s ap ap b ap b ap cons 0 ap ap c ap ap b b cons ap ap c cons nil ap ap c cons nil ap c cons
""".strip()

i = Interaction(data, "statefuldraw")
i(4, 8)
i(7, 7)
i(12, 14)
