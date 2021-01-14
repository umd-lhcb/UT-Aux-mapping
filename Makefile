# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Thu Jan 14, 2021 at 12:40 PM +0100

export PATH	:= $(shell pwd):$(PATH)

OUTPUT_PATH	:=	output
VPATH := $(OUTPUT_PATH)

#########
# Rules #
#########

.PHONY: all
all: \
	P2B2toPPP-C-TOP-MAG-TRUE-Alpha.pdf \
	P2B2toPPP-C-TOP-MAG-TRUE-Beta.pdf \
	P2B2toPPP-C-TOP-MAG-TRUE-Gamma.pdf \
	P2B2toPPP-C-BOT-MAG-MIRROR-Alpha.pdf \
	P2B2toPPP-C-BOT-MAG-MIRROR-Beta.pdf \
	P2B2toPPP-C-BOT-MAG-MIRROR-Gamma.pdf \
	P2B2toPPP-C-TOP-IP-MIRROR-Alpha.pdf \
	P2B2toPPP-C-TOP-IP-MIRROR-Beta.pdf \
	P2B2toPPP-C-TOP-IP-MIRROR-Gamma.pdf

.PHONY: clean
clean:
	@rm -rf $(OUTPUT_PATH)/*

P2B2toPPP-C-TOP-MAG-TRUE-Alpha.csv P2B2toPPP-C-TOP-MAG-TRUE-Beta.csv P2B2toPPP-C-TOP-MAG-TRUE-Gamma.csv \
P2B2toPPP-C-TOP-MAG-TRUE-Alpha.tex P2B2toPPP-C-TOP-MAG-TRUE-Beta.tex P2B2toPPP-C-TOP-MAG-TRUE-Gamma.tex &: \
	TrueP2B2toPPPMapping.py UT_Aux_mapping/helpers.py UT_Aux_mapping/tabular.py \
	input/true_p2b2.net input/true_ppp.wirelist
	$<

P2B2toPPP-C-BOT-MAG-MIRROR-Alpha.csv P2B2toPPP-C-BOT-MAG-MIRROR-Beta.csv P2B2toPPP-C-BOT-MAG-MIRROR-Gamma.csv \
P2B2toPPP-C-TOP-IP-MIRROR-Alpha.csv P2B2toPPP-C-TOP-IP-MIRROR-Beta.csv P2B2toPPP-C-TOP-IP-MIRROR-Gamma.csv \
P2B2toPPP-C-BOT-MAG-MIRROR-Alpha.tex P2B2toPPP-C-BOT-MAG-MIRROR-Beta.tex P2B2toPPP-C-BOT-MAG-MIRROR-Gamma.tex \
P2B2toPPP-C-TOP-IP-MIRROR-Alpha.tex P2B2toPPP-C-TOP-IP-MIRROR-Beta.tex P2B2toPPP-C-TOP-IP-MIRROR-Gamma.tex &: \
	MirrorP2B2toPPPMapping.py UT_Aux_mapping/helpers.py UT_Aux_mapping/tabular.py \
	input/mirror_p2b2.net input/mirror_ppp.wirelist
	$<


####################
# Generic patterns #
####################

%.pdf: %.tex
	@pdflatex -output-directory $(OUTPUT_PATH) $<
	@pdflatex -output-directory $(OUTPUT_PATH) $<
