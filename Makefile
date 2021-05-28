# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Fri May 28, 2021 at 03:39 AM +0200

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
	P2B2toPPP-C-BOT-IP-TRUE-Alpha.pdf \
	P2B2toPPP-C-BOT-IP-TRUE-Beta.pdf \
	P2B2toPPP-C-BOT-IP-TRUE-Gamma.pdf \
	P2B2toPPP-C-BOT-MAG-MIRROR-Alpha.pdf \
	P2B2toPPP-C-BOT-MAG-MIRROR-Beta.pdf \
	P2B2toPPP-C-BOT-MAG-MIRROR-Gamma.pdf \
	P2B2toPPP-C-TOP-IP-MIRROR-Alpha.pdf \
	P2B2toPPP-C-TOP-IP-MIRROR-Beta.pdf \
	P2B2toPPP-C-TOP-IP-MIRROR-Gamma.pdf \
	P2B2toPPP-A-TOP-IP-TRUE-Alpha.pdf \
	P2B2toPPP-A-TOP-IP-TRUE-Beta.pdf \
	P2B2toPPP-A-TOP-IP-TRUE-Gamma.pdf \
	P2B2toPPP-A-BOT-MAG-TRUE-Alpha.pdf \
	P2B2toPPP-A-BOT-MAG-TRUE-Beta.pdf \
	P2B2toPPP-A-BOT-MAG-TRUE-Gamma.pdf \
	P2B2toPPP-A-BOT-IP-MIRROR-Alpha.pdf \
	P2B2toPPP-A-BOT-IP-MIRROR-Beta.pdf \
	P2B2toPPP-A-BOT-IP-MIRROR-Gamma.pdf \
	P2B2toPPP-A-TOP-MAG-MIRROR-Alpha.pdf \
	P2B2toPPP-A-TOP-MAG-MIRROR-Beta.pdf \
	P2B2toPPP-A-TOP-MAG-MIRROR-Gamma.pdf \

.PHONY: clean
clean:
	@rm -rf $(OUTPUT_PATH)/*

P2B2toPPP-C-TOP-MAG-TRUE-Alpha.csv P2B2toPPP-C-TOP-MAG-TRUE-Beta.csv P2B2toPPP-C-TOP-MAG-TRUE-Gamma.csv \
P2B2toPPP-C-TOP-MAG-TRUE-Alpha.tex P2B2toPPP-C-TOP-MAG-TRUE-Beta.tex P2B2toPPP-C-TOP-MAG-TRUE-Gamma.tex \
P2B2toPPP-C-BOT-IP-TRUE-Alpha.csv P2B2toPPP-C-BOT-IP-TRUE-Beta.csv P2B2toPPP-C-BOT-IP-TRUE-Gamma.csv \
P2B2toPPP-C-BOT-IP-TRUE-Alpha.tex P2B2toPPP-C-BOT-IP-TRUE-Beta.tex P2B2toPPP-C-BOT-IP-TRUE-Gamma.tex \
P2B2toPPP-C-BOT-MAG-MIRROR-Alpha.csv P2B2toPPP-C-BOT-MAG-MIRROR-Beta.csv P2B2toPPP-C-BOT-MAG-MIRROR-Gamma.csv \
P2B2toPPP-C-BOT-MAG-MIRROR-Alpha.tex P2B2toPPP-C-BOT-MAG-MIRROR-Beta.tex P2B2toPPP-C-BOT-MAG-MIRROR-Gamma.tex \
P2B2toPPP-C-TOP-IP-MIRROR-Alpha.csv P2B2toPPP-C-TOP-IP-MIRROR-Beta.csv P2B2toPPP-C-TOP-IP-MIRROR-Gamma.csv \
P2B2toPPP-C-TOP-IP-MIRROR-Alpha.tex P2B2toPPP-C-TOP-IP-MIRROR-Beta.tex P2B2toPPP-C-TOP-IP-MIRROR-Gamma.tex \
P2B2toPPP-A-BOT-MAG-TRUE-Alpha.csv P2B2toPPP-A-BOT-MAG-TRUE-Beta.csv P2B2toPPP-A-BOT-MAG-TRUE-Gamma.csv \
P2B2toPPP-A-BOT-MAG-TRUE-Alpha.tex P2B2toPPP-A-BOT-MAG-TRUE-Beta.tex P2B2toPPP-A-BOT-MAG-TRUE-Gamma.tex \
P2B2toPPP-A-TOP-IP-TRUE-Alpha.csv P2B2toPPP-A-TOP-IP-TRUE-Beta.csv P2B2toPPP-A-TOP-IP-TRUE-Gamma.csv \
P2B2toPPP-A-TOP-IP-TRUE-Alpha.tex P2B2toPPP-A-TOP-IP-TRUE-Beta.tex P2B2toPPP-A-TOP-IP-TRUE-Gamma.tex \
P2B2toPPP-A-TOP-MAG-MIRROR-Alpha.csv P2B2toPPP-A-TOP-MAG-MIRROR-Beta.csv P2B2toPPP-A-TOP-MAG-MIRROR-Gamma.csv \
P2B2toPPP-A-TOP-MAG-MIRROR-Alpha.tex P2B2toPPP-A-TOP-MAG-MIRROR-Beta.tex P2B2toPPP-A-TOP-MAG-MIRROR-Gamma.tex \
P2B2toPPP-A-BOT-IP-MIRROR-Alpha.csv P2B2toPPP-A-BOT-IP-MIRROR-Beta.csv P2B2toPPP-A-BOT-IP-MIRROR-Gamma.csv \
P2B2toPPP-A-BOT-IP-MIRROR-Alpha.tex P2B2toPPP-A-BOT-IP-MIRROR-Beta.tex P2B2toPPP-A-BOT-IP-MIRROR-Gamma.tex \
&: \
	P2B2toPPPMapping.py UT_Aux_mapping/helpers.py UT_Aux_mapping/tabular.py \
	input/true_p2b2.net input/mirror_p2b2.net \
	input/c_true_ppp_mag.wirelist input/c_true_ppp_ip.wirelist \
	input/c_mirror_ppp_mag.wirelist input/c_mirror_ppp_ip.wirelist
	$<


####################
# Generic patterns #
####################

%.pdf: %.tex
	@pdflatex -output-directory $(OUTPUT_PATH) $<
	@pdflatex -output-directory $(OUTPUT_PATH) $<
