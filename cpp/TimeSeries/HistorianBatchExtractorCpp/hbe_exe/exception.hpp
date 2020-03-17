#pragma once

//+-------------------------------------------------------------------------------------------------
//! Defines an pre-built exception .
//+-------------------------------------------------------------------------------------------------
#define HISTORIAN_EXCEPTION(x) historian::Exception(__FILE__, __LINE__, x)

namespace historian
{
    //+---------------------------------------------------------------------------------------------
    //! \brief		Defines an exception.
    //+---------------------------------------------------------------------------------------------
    class Exception
    {
    public:
        //! Constructs from a file, a line and a comment.
        Exception(std::string const& file, int line, std::string const& comment) :
            m_file(file),
            m_line(line),
            m_message(comment)
        {
        }

		//! Constructs from a file, a line and aw exception.
		Exception(std::string const& file, int line, const std::exception& e) :
			m_file(file),
			m_line(line),
			m_message(e.what())
		{
		}

        //! Destroys.
        ~Exception(void)
        {
        }

        //! Gets the file name where the exception is thrown.
        std::string getOrigineFile(void) const
        {
            return m_file;
        }

        //! Gets the line index where the exception is thrown.
        int getOrigineLine(void) const
        {
            return m_line;
        }

		//! Delivers the message with addtional informations.
		std::string getFullMessage(void) const
		{
			return "File : " + m_file + ", Line : " + std::to_string(m_line) + ", " + m_message;
		}

        //! Delivers the message.
        std::string getMessage(void) const
        {
            return m_message;
        }

        //! Adds another message.
        void addMessage(std::string const& comment)
        {
            m_message += comment;
        }

    private:
        Exception(void) = delete;

    protected:
        std::string m_file;
		int m_line;
        std::string m_message;
    };
}
