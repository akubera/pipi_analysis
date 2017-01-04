#
# Makefile
#
# Identical pion makefile
#

ALIROOT = aliroot


.PHONY: all run run_grid clean


all:


run: RunMe.C
	aliroot -q -x $< 2

multi_run:
	for i in {1..8}; do aliroot -q -x src/RunLocal.C $$i & sleep 4; done

run_local:
	for i in {1..8}; do aliroot -q -x src/RunLocal.C $$i & sleep 4; done

multi_run_11:
	for i in {1..8}; do aliroot -q -x src/RunParallel_11.C $$i TEMP_RESULT.root & sleep 4; done

run_grid: RunGrid.C
	aliroot -q -x $<

run-mc:
	aliroot -q -x src/RunMC.C

%.C: src/%.C
	cp $< $@


clean:
	rm -rf *.o AutoDict*
