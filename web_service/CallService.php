<?php
/**
 * Author : Yrol Fernando
 * Date created : 14/09/13
 * Specs: Retreive exhibit information
 * */
require_once("Connect.php");

class CallService
{
	//variables holding the information
	private $info_ID;
	private $connection;
	private $stmt;
	private $response = array();
	
	//constructor accepting the arguments and structure the program
	function __construct()
	{
		if(isset($_POST['info_ID']))
		{
			$info_ID = $_POST['info_ID'];
			
			/*
			//check existence of info
			$this->checkDataExistence($info_ID);
			
			//Retrieve data
			$this->RetrieveInformation($info_ID);
			* */
			echo "Good";
		}
		else
		{
			$this->response["success"] = "0";
			$this->response["message"] = "An error occurred";
			die(json_encode($this->response));
		}
	}
	
	//retrieve information 
	function RetrieveInformation($id)
	{
		$this->connection = new Connect();
		$info = array();
		
		//join statement
		$query = "SELECT * from exhibit_info";
		
		if($this->stmt = $this->connection->connect_to_db()->prepare($query))
		{
			$this->stmt->execute();
			
			$this->stmt->store_result();
			
			echo($this->stmt->num_rows);
		}
		else
		{
			$this->response["success"] = 0;
			$this->response["message"] = "Connection error, Please try again later";
			die(json_encode($this->response));
		}
	}
	
	//check existence of data or kil the script
	function checkDataExistence($id)
	{	
		$num_rows = 1;
		
		if($num_rows == 0)
		{
			$this->response["success"] = 0;
			$this->response["message"] = "Info does not exist";
			die(json_encode($this->response));
		}
	}
	
	//destructor closing the connection
	function __destruct()
	{
		if(isset($this->stmt))
		{
			$this->stmt->close();
		}
	}
}

//create objects
$object  = new CallService();
// $object->RetrieveInformation();

?>
