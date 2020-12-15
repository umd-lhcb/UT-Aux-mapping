# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Tue Dec 15, 2020 at 04:22 PM +0100

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
	MirrorP2B2toPPPMappingFull.pdf \
	MirrorP2B2toPPPMappingPartial.pdf \
	MirrorP2B2toPPPMappingDepopulated.pdf

.PHONY: clean
clean:
	@rm -rf $(OUTPUT_PATH)/*

P2B2toPPP-C-TOP-MAG-TRUE-Alpha.csv P2B2toPPP-C-TOP-MAG-TRUE-Beta.csv P2B2toPPP-C-TOP-MAG-TRUE-Gamma.csv \
P2B2toPPP-C-TOP-MAG-TRUE-Alpha.tex P2B2toPPP-C-TOP-MAG-TRUE-Beta.tex P2B2toPPP-C-TOP-MAG-TRUE-Gamma.tex &: \
	TrueP2B2toPPPMapping.py UT_Aux_mapping/helpers.py UT_Aux_mapping/tabular.py \
	input/true_p2b2.net input/true_ppp.wirelist
	$<

MirrorP2B2toPPPMappingFull.csv MirrorP2B2toPPPMappingPartial.csv MirrorP2B2toPPPMappingDepopulated.csv \
MirrorP2B2toPPPMappingFull.tex MirrorP2B2toPPPMappingPartial.tex MirrorP2B2toPPPMappingDepopulated.tex &: \
	MirrorP2B2toPPPMapping.py UT_Aux_mapping/helpers.py UT_Aux_mapping/tabular.py \
	input/true_p2b2.net input/true_ppp.wirelist
	$<


####################
# Generic patterns #
####################

%.pdf: %.tex
	@pdflatex -output-directory $(OUTPUT_PATH) $<
