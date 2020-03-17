#pragma once

#include "historian.hpp"

namespace historian
{
	class Connection
	{
	public:
		static Connection& getInstance()
		{
			return m_instance;
		}

		void initialize(std::string server) {
			m_server = server;
		}

		void initialize(std::string server, std::string user, std::string pwd) {
			m_server = server;
			m_user = user;
			m_pwd = pwd;
		}

		long getHandle() {
			if (m_handle < 0) connect();
			return m_handle;
		}

		void connect();
		void close();

	private:
		// singleton instance
		static Connection m_instance;

		// constructor
		Connection() : m_server(), m_user(), m_pwd(), m_handle(-1) {}
		~Connection() {
			try
			{
				close();
			}
			catch (...)
			{
				LOG_WARN("error met when trying to close connection to ", m_server);
			}
		}

		std::string m_server;
		std::string m_user;
		std::string m_pwd;
		long m_handle;
	};
}