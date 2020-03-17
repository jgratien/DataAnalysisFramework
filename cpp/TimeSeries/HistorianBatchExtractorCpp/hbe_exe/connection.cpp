#include "connection.hpp"

namespace historian
{
	Connection Connection::m_instance;

	void Connection::connect() {
		if (m_handle > 0) return;
		if (m_instance.m_server.size() == 0) throw HISTORIAN_EXCEPTION("you have to initialize connection first");
		// connect to default server with logged in user
		char* server = TO_CSTR(m_server);
		char* user = TO_CSTR(m_user);
		char* pwd = TO_CSTR(m_pwd);
		long return_code(ihuConnect(server, user, pwd, &m_handle));
		// Set properties necessary for migration
		if (return_code != ihuSTATUS_OK)
		{
			m_handle = -1;
			throw HISTORIAN_EXCEPTION(MiscUtils::to_string("error met when trying to connect to ", m_server));
		}
	}

	void Connection::close() {
		if (m_handle < 0) return;
		try
		{
			ihuDisconnect(m_handle);
			LOG_DEBUG("Connection close to ", m_server);
		}
		catch (...)
		{
			LOG_WARN("Error met when trying to close connection to ", m_server);
		}
		m_handle = -1;
	}
}