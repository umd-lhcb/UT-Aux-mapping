# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Mon Dec 14, 2020 at 04:13 PM +0100

export PATH	:= $(shell pwd):$(PATH)

OUTPUT_PATH	:=	output
VPATH := $(OUTPUT_PATH)

#########
# Rules #
#########

.PHONY: all
all: TrueP2B2toPPPMappingFull.pdf \
	TrueP2B2toPPPMappingPartial.pdf \
	TrueP2B2toPPPMappingDepopulated.pdf

.PHONY: clean
clean:
	@rm -rf $(OUTPUT_PATH)/*

TrueP2B2toPPPMappingFull.csv TrueP2B2toPPPMappingPartial.csv TrueP2B2toPPPMappingDepopulated.csv \
TrueP2B2toPPPMappingFull.tex TrueP2B2toPPPMappingPartial.tex TrueP2B2toPPPMappingDepopulated.tex &: \
	TrueP2B2toPPPMapping.py UT_Aux_mapping/helpers.py UT_Aux_mapping/tabular.py \
	input/true_p2b2.net input/true_ppp.wirelist
	$<


####################
# Generic patterns #
####################

%.pdf: %.tex
	@pdflatex -output-directory $(OUTPUT_PATH) $<
