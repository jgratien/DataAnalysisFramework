package fr.ifpen.historian.db;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import fr.ifpen.historian.config.Database;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.utils.HistorianExtractorException;
import liquibase.Contexts;
import liquibase.LabelExpression;
import liquibase.Liquibase;
import liquibase.database.DatabaseFactory;
import liquibase.database.jvm.JdbcConnection;
import liquibase.exception.DatabaseException;
import liquibase.exception.LiquibaseException;
import liquibase.resource.ClassLoaderResourceAccessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.SQLException;

public class DataSource {

    private static Logger log = LoggerFactory.getLogger(DataSource.class);

    private static DataSource instance;

    private HikariDataSource ds;

    private DataSource() {
    }

    public static DataSource getInstance() {
        if (instance == null) {
            instance = new DataSource();
        }
        return instance;
    }

    // in daemon mode (ie service mode) we need to create or update db structure (tables, index, ...)
    // in other case, we just want to get connections
    public void initialize(boolean daemonMode) {
        // create datasource pool
        initializePool();
        if (daemonMode) {
            // create database structure with liquibase framework
            createOrUpdateDatabase();
        }
    }

    public Connection getConnection() throws SQLException {
        log.debug("getting database connection");
        if (ds == null || !ds.isRunning()) {
            throw new HistorianExtractorException("Database not started, connection not allowed");
        }
        return ds.getConnection();
    }

    public void close() {
        log.debug("trying to close database connection pool");
        if (ds != null && ds.isRunning()) {
            ds.close();
            if (ds.isClosed()) {
                log.debug("database connection pool has been successfully closed");
            } else {
                log.warn("unable to close Database connection pool");
            }
            ds = null;
        }
    }

    private void initializePool() {
        // create database connection pool with hikaricp framework
        Database database = Singleton.getInstance().getConfiguration().getDatabase();
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(database.getUrl());
        config.setUsername(database.getUsername());
        config.setPassword(database.getPassword());
        config.addDataSourceProperty("cachePrepStmts", database.getCachePrepStmts().toString());
        config.addDataSourceProperty("prepStmtCacheSize", database.getPrepStmtCacheSize().toString());
        config.addDataSourceProperty("prepStmtCacheSqlLimit", database.getPrepStmtCacheSqlLimit().toString());
        ds = new HikariDataSource(config);
    }

    private void createOrUpdateDatabase() {
        try (Connection conn = DataSource.getInstance().getConnection()) {
            liquibase.database.Database database = DatabaseFactory.getInstance().findCorrectDatabaseImplementation(new JdbcConnection(conn));
            Liquibase liquibase = new Liquibase("liquibase/master.xml", new ClassLoaderResourceAccessor(), database);
            liquibase.update(new Contexts(), new LabelExpression());
        } catch (SQLException e) {
            log.error("database connection on error: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode(), e);
            throw new HistorianExtractorException(e);
        } catch (DatabaseException e) {
            log.error("database initialization with liquibase on error: {}", e.getMessage(), e);
            throw new HistorianExtractorException(e);
        } catch (LiquibaseException e) {
            log.error("database liquibase configuration is invalid: {}", e.getMessage(), e);
            throw new HistorianExtractorException(e);
        }
    }
}