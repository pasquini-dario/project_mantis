import time
import shutil
import subprocess

from ..utils.logger import logger

class IP_blocker:

	def __init__(self, decoy_ports=None):
		import iptc
		self.iptc = iptc
		self.ip_jails = set()
		self.decoy_ports = decoy_ports or []
		# Unique comment tag to mark rules added by this instance
		self.rule_comment = f"IP_BLOCKER_{id(self)}"

	def add_decoy_port(self, decoy_port):
		logger.info(
			f"Adding port {decoy_port} to the list of allowed ports when partial IP blocking is active"
		)
		self.decoy_ports.append(decoy_port)

	def jail_ip(self, ip):
		if ip in self.ip_jails:
			return
		logger.warning(
			f"Blocking IP {ip} except for ports {', '.join(map(str, self.decoy_ports))}"
		)
		self.ip_jails.add(ip)
		self._block_all_except_ports(list(self.decoy_ports), ip)

	def cleanup(self):
		logger.warning(f"Cleaning all iptables rules added by IP_blocker instance")
		self._reset_instance_rules()

	def __del__(self):
		self.cleanup()

	@staticmethod
	def is_iptables_installed():
		if shutil.which("iptables"):
			return True
		try:
			subprocess.run(
				["iptables", "--version"],
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL,
				check=True,
			)
			return True
		except (FileNotFoundError, subprocess.CalledProcessError):
			return False

	def commit_with_retry(self, table, retries=5, delay=0.1):
		for attempt in range(retries):
			try:
				table.commit()
				return
			except self.iptc.IPTCError as e:
				if 'Resource temporarily unavailable' in str(e):
					time.sleep(delay)
				else:
					raise
		raise self.iptc.IPTCError(
			f"Could not acquire xtables lock after {retries} retries"
		)

	def _block_all_except_ports(self, allowed_ports, ip, chain_name="INPUT", protocol="tcp"):
		table = self.iptc.Table(self.iptc.Table.FILTER)
		table.refresh()
		table.autocommit = False

		try:
			chain = self.iptc.Chain(table, chain_name)
			# Add ACCEPT rules for allowed ports with comment
			for port in allowed_ports:
				rule = self.iptc.Rule()
				rule.src = ip
				rule.protocol = protocol
				match = rule.create_match(protocol)
				match.dport = str(port)
				rule.target = rule.create_target("ACCEPT")
				# Add comment
				comment = rule.create_match("comment")
				comment.comment = self.rule_comment
				chain.append_rule(rule)

			# Add DROP rule with comment
			drop_rule = self.iptc.Rule()
			drop_rule.src = ip
			drop_rule.target = drop_rule.create_target("DROP")
			comment = drop_rule.create_match("comment")
			comment.comment = self.rule_comment
			chain.append_rule(drop_rule)

			self.commit_with_retry(table)
		finally:
			table.autocommit = True

	def _reset_instance_rules(self, chain_name="INPUT"):
		table = self.iptc.Table(self.iptc.Table.FILTER)
		table.refresh()
		table.autocommit = False

		try:
			chain = self.iptc.Chain(table, chain_name)
			# Iterate rules and remove those with our comment
			for rule in list(chain.rules):  # make copy since we'll modify
				for match in rule.matches:
					if match.name == 'comment' and getattr(match, 'comment', None) == self.rule_comment:
						chain.delete_rule(rule)
						break
			self.commit_with_retry(table)
		finally:
			table.autocommit = True