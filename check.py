#!/usr/bin/env python3

import sys
import time

CL_RED = '\033[1;31m'
CL_GREEN = '\033[1;32m'
CL_YELLOW = '\033[1;33m'
CL_BLUE = '\033[1;34m'
CL_PURPLE = '\033[1;34m'
CL_NONE = '\033[0m'

DELETE_MANIPULATOR = 'del'

class Student(object):
	def __init__(self, stuid, name, line_in_names, pt=''):
		self._stuid = stuid
		self._name = name
		self._pt = pt
		self.line_in_names = line_in_names 
		self.check_seq = -1

	def has_pt(self):
		return self._pt != ''

	def set_pt(self, pt, seq):
		self._pt = pt
		self.check_seq = seq

	def __str__(self):
		return '%s%s\t%s\t%s%s' % (self.has_pt() and CL_GREEN or CL_RED, self._stuid, self._name, self.has_pt() and str(self._pt) or 'Not checked', CL_NONE)

def read_names():
	print('Reading names')

	fin = open('namelist.csv', 'r')
	if not fin:	return None

	students = {}
	lc = 0
	while True:
		line = fin.readline()
		if not line:	break
		lc += 1
		sys.stdout.write('\rReading line: %d' % lc)
		
		items = [ item for item in line.strip().split(',') if item != '' ]

		if len(items) != 2 and len(items) != 3:
			print('\n\tInvalid line: %s' % line.strip())
			return None

		stuid = items[0]
		stuname = items[1]

		pt = len(items) == 3 and items[2]

		if stuid in students:
			print('\nWarning: same student ID: %s in line %d, skipping' % (stuid, students[stuid].line_in_names))
			continue

		students[stuid] = pt and Student(stuid, stuname, lc, pt) or Student(stuid, stuname, lc)

	print()
	
	return students

def show_students(students):
	for stu in students.values():
		print(stu)
	print()

# By default, only match ID which has suffix
# However, sometimes, we need to check if the given short name is only a substring
def find_student(students, stuname_short, substr_match=False):
	return substr_match\
		and [stuid for stuid in students.keys() if stuname_short in stuid]\
		or [stuid for stuid in students.keys() if stuid.endswith(stuname_short)]

def choose_from(students, candidates, indenttab=2):
	prefix = '\t' * indenttab
	print('%s0. %s(Cancel)%s' % (prefix, CL_PURPLE, CL_NONE))
	for i in range(len(candidates)):
		try:
			print('%s%d. %s' % (prefix, i+1, students[candidates[i]]))
		except KeyError:
			print('%s%s%d. Unexpected non-existing student ID: %s%s' % (prefix, CL_BLUE, i+1, candidates[i], CL_NONE))
	while True:
		try:
			subcmd = input('%s>> ' % prefix)
		except EOFError:
			return -1

		ok = False
		try:
			cmd = int(subcmd)
			if cmd >= 0 and cmd <= len(candidates):
				return cmd - 1
		except:
			pass

		print('%sUnknown selection %s' % (prefix, subcmd))

def give_points(students, stuid, score, check_seq, fj):
	timestr = time.asctime(time.localtime())
	try:
		assert(stuid in students)
	except AssertionError:
		fj.write('%s  Fatal: student ID %s not found. Skipping' % (timestr, stuid))
		fj.flush()
		return False
	
	updated = False
	stu = students[stuid]
	if stu.has_pt():
		delta_seq = check_seq - stu.check_seq
		cmd = input(' %sFatal: Student %s %s already has score %s%s %s%d%s checks ago! %s?%s [y/N]: ' % (CL_RED, stuid, stu._name, CL_GREEN, stu._pt, CL_YELLOW, delta_seq, CL_RED, score and 'overwrite' or 'delete', CL_NONE))
		if cmd == 'y' or cmd == 'Y':
			if not score:
				fj.write('%s Delete %s %s: %s\n' % (timestr, stuid, stu._name, stu._pt))
				print(' %sDelete %s %s: %s%s%s' % (CL_PURPLE, stuid, stu._name, CL_RED, stu._pt, CL_NONE))
			else:
				fj.write('%s Overwrite %s %s: %s->%s\n' % (timestr, stuid, stu._name, stu._pt, score))
				print(' %sOverwrite %s %s: %s%s%s->%s%s%s' % (CL_PURPLE, stuid, stu._name, CL_RED, stu._pt, CL_PURPLE, CL_GREEN, score, CL_NONE))
			updated = True
			stu.set_pt(score, check_seq)
		else:
			if not score:
				fj.write('%s Skipped deletion for student %s %s, who already has score %s %d checks ago.\n' % (timestr, stuid, stu._name, stu._pt, delta_seq))
				print(' %sSkipped deletion for student %s %s, who already has score %s%s %s%d%s checks ago.%s' % (CL_PURPLE, stuid, stu._name, CL_GREEN, stu._pt, CL_YELLOW, delta_seq, CL_PURPLE, CL_NONE))
			else:
				fj.write('%s Skipped score %s for the same student %s %s, who already has score %s %d checks ago.\n' % (timestr, score, stuid, stu._name, stu._pt, delta_seq))
				print(' %sSkipped score %s%s%s for student %s %s, who already has score %s%s %s%d%s checks ago.%s' % (CL_PURPLE, CL_RED, score, CL_PURPLE, stuid, stu._name, CL_GREEN, stu._pt, CL_YELLOW, delta_seq, CL_PURPLE, CL_NONE))
	else:
		if not score:
			fj.write('%s Skipped deletion for student %s %s, who has no score recorded.\n' % (timestr, stuid, stu._name))
			print(' %sSkipped deletion for student %s %s, who has no score recored.%s' % (CL_PURPLE, stuid, stu._name, CL_NONE))
			stu.set_pt(score, check_seq)
		else:
			fj.write('%s Give %s %s: %s\n' % (timestr, stuid, stu._name, score))
			print(' %sGive %s %s: %s%s%s' % (CL_YELLOW, stuid, stu._name, CL_GREEN, score, CL_NONE))
			stu.set_pt(score, check_seq)
			updated = True

	fj.flush()
	return updated

def main_loop(students):
	fj = open('journal.txt', 'a')
	fout = open('scores.csv', 'w')

	check_seq = 0
	total_num = len(students.keys())
	while True:
		# Count ratio
		checked = sum(1 for stu in students.values() if stu.has_pt())
		print('\n%sChecked: %s%d%s / %s%d%s' % (CL_BLUE, CL_GREEN, checked, CL_NONE, CL_YELLOW, total_num, CL_NONE))

		try:
			cmdstr = input('> ')
		except EOFError:
			print()
			break
		if not cmdstr:	continue
	
		cmd = cmdstr.split()
		if len(cmd) == 1 and cmd[0] == 'q' or cmd[0] == 'quit' or cmd[0] == 'exit':	break

		if len(cmd) == 1 and cmd[0] == 's':
			show_students(students)
			continue

		if len(cmd) == 2:
			candidates = find_student(students, cmd[0])

			# Override delete command with empty score
			if cmd[1].lower() == DELETE_MANIPULATOR:	cmd[1] = ''

			if len(candidates) == 0:
				loosen_candidates = find_student(students, cmd[0], True)
				if len(loosen_candidates) == 0:
					print('\tError: No students with substring %s found' % cmd[0])
				else:
					print('\tNo students with suffix %s found, but some students\' IDs found with substring:', cmd[0])
					index = choose_from(students, loosen_candidates)
					if index >= 0:
						check_seq += give_points(students, loosen_candidates[index], cmd[1], check_seq, fj) and 1 or 0
			elif len(candidates) == 1:
				check_seq += give_points(students, candidates[0], cmd[1], check_seq, fj) and 1 or 0
			else:
				print('\tMultiple students\' IDs found with suffix %s' % cmd[0])
				index = choose_from(students, candidates)
				if index >= 0:
					check_seq += give_points(students, candidates[index], cmd[1], check_seq, fj) and 1 or 0

		else:
			print('\t%sInvalid command: %s%s' % (CL_PURPLE, cmdstr, CL_NONE))

	fj.close()

	for stu in sorted(list(students.values()), key=lambda stu: stu.line_in_names):
		fout.write('%s,%s,%s\n' % (stu._stuid, stu._name, stu._pt))

	fout.close()

def main():
	students = read_names()
	if not students:	return 1

	#show_students(students)
	main_loop(students)

	return 0

if __name__ == '__main__':
	sys.exit(main())
