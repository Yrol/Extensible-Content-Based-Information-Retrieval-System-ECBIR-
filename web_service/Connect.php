<?php
class Connect
{
	private $server = "localhost";
	private $user = "root";
	private $password = "";
	private $database = "Android";
	private $connection;
	
	//connect to the database 
	function connect_to_db(){
		
		$this->connection = new mysqli($this->server, $this->user, $this->password, $this->database);
		
		if(@mysqli_connect_errno()){
			
			echo $this->connection = "Could not connect to the database".@mysqli_connect_errno();
		}
		return $this->connection;
	}
	
	//close connection
	function __destruct()
	{
		mysqli_close($this->connection);
	}
}
?>

