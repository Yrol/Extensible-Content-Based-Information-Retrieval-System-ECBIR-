package com.simplecv.hellocamera;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.mime.MultipartEntity;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.entity.mime.content.StringBody;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Spinner;
import android.widget.Toast;

public class MuseumGuideMainActivity extends Activity {

	private static final int TAKE_PICTURE = 0;
	private static final int SELECT_PICTURE = 1;
	private boolean pictureIsSet = false;

	//Default - 10.0.2.2
	//ifconfig - inet addr:192.168.1.68
	private static String uploadURL = "http://192.168.1.68:8000/upload";
	private static String modifyURL = "http://192.168.1.68:8000/process";

	private ImageView capturedImage;
	private Uri pictureUri;
	private Bitmap pictureBitmap;
	private String pathToPicture;
	private Button goButton;
	private Button clockwiseButton;
	private Button counterclockwiseButton;

	private String linkToOriginal = null;
	private int rotation;
	
	private String transformedImageURL = null;
	private HttpEntity responseEntity = null;
	String[] results = new String[10];
	
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        capturedImage = (ImageView) findViewById(R.id.capturedimage);
        goButton = (Button) findViewById(R.id.go_button);
        counterclockwiseButton = (Button) findViewById(R.id.counterclockwise_button);
        clockwiseButton = (Button) findViewById(R.id.clockwise_button);
    }

    //get the picture from the picture gallery
    public File getNewPictureFile(){
		File mediaStorageDir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES), "SimpleCV");
		if (!mediaStorageDir.exists()){
			if (!mediaStorageDir.mkdirs()){
				Log.i("SimpleCV", "Failed to create directory");
		    	mediaStorageDir = Environment.getExternalStorageDirectory();
	        }
	    }

        String timeStamp = new SimpleDateFormat("MMdd_HHmmss").format(new Date());
        File file = new File(mediaStorageDir.getPath() + File.separator + "IMG_" + timeStamp + ".jpg");
    	return file;
    }
    
    //location of the image
    public Uri getUriFromBitmap(Bitmap bitmap) {
		File newPictureFile = getNewPictureFile();
		try {
	        FileOutputStream outStream = new FileOutputStream(newPictureFile);
	        bitmap.compress(Bitmap.CompressFormat.JPEG,100, outStream);
	        outStream.flush();
	        outStream.close();
		}
		catch(Exception e) {
			e.printStackTrace();
		}
        return Uri.fromFile(newPictureFile);
    }
    
    //Decoding the Bitmap  files in order to make them suitable to submit to the server
    public Bitmap decodeFile(File f){
        Bitmap b = null;
        try {
            BitmapFactory.Options o = new BitmapFactory.Options();
            o.inJustDecodeBounds = true;

            FileInputStream fis = new FileInputStream(f);
            BitmapFactory.decodeStream(fis, null, o);
            fis.close();

            int scale = 1;
            if (o.outHeight > 300 || o.outWidth > 300) { //Max size = ?
                scale = (int)Math.pow(2, (int) Math.round(Math.log(300 / (double) Math.max(o.outHeight, o.outWidth)) / Math.log(0.5)));
            }

            BitmapFactory.Options o2 = new BitmapFactory.Options();
            o2.inSampleSize = scale;
            fis = new FileInputStream(f);
            b = BitmapFactory.decodeStream(fis, null, o2);
            fis.close();
        } catch (IOException e) {
        	e.printStackTrace();
        }
        return b;
    }
    
    public void refreshImage() {
    	capturedImage.setImageBitmap(pictureBitmap);
    }
    
    public void displayPicture(){
    	pictureBitmap = decodeFile(new File(pathToPicture));
    	forcePortrait();
    	if (rotation == 0) refreshImage();
    }

	public void takePicture(View view){

    	Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
    	pictureUri = Uri.fromFile(getNewPictureFile());
    	intent.putExtra(MediaStore.EXTRA_OUTPUT, pictureUri);
    	startActivityForResult(intent, TAKE_PICTURE);
    }

    public void selectPicture(View view){
    	Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
    	intent.setType("image/*");
    	startActivityForResult(Intent.createChooser(intent,"Select an image"),SELECT_PICTURE);
    }


    public String getPathFromGallery(Uri uri) {
    	Cursor cursor = getContentResolver().query(uri, null, null, null, null);
        cursor.moveToFirst();
        int idx = cursor.getColumnIndex(MediaStore.Images.ImageColumns.DATA);
        return cursor.getString(idx);
    }
    
    //Check the network availability
    private boolean isNetworkAvailable() {
        ConnectivityManager connectivityManager 
              = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeNetworkInfo = connectivityManager.getActiveNetworkInfo();
        return activeNetworkInfo != null && activeNetworkInfo.isConnectedOrConnecting();
    }
    
    //Execute when the go button is pressed
    public void processPicture(View view) {
    	if (isNetworkAvailable()) {
    		if (pictureIsSet) {
			  		new UploadImageTask(this).execute();
    		}
    	} else {
    		Toast.makeText(getApplicationContext(), 
                    "No internet connection!", Toast.LENGTH_LONG).show();	
    	}
    }
    
    //Handle asynchronous tasks happening @ the background when submitting and retrieving information
    private class UploadImageTask extends AsyncTask<Void, String, Void> {
    	
    	private Context context;
    	ProgressDialog progressDialog;
		    
    	public UploadImageTask(Context cxt) {
            context = cxt;
            progressDialog = new ProgressDialog(context);
        }
    	
    	
    	protected void onPreExecute() {
    		progressDialog.setMessage("Preparing picture...");
    		progressDialog.show();
        }	
    	
        protected Void doInBackground(Void... unused) {
        	
    		if (linkToOriginal == null) {
	        	this.publishProgress("Uploading picture...");
    			uploadPicture();
    		}
    		
        	this.publishProgress("Getting picture back...");
			modifyPicture();
    		
			//call the resources free function
			return (null);
        }
        
        protected void onPostExecute(Void unused) {
        	progressDialog.dismiss();
        	//Toast.makeText(getApplicationContext(),results[0], Toast.LENGTH_LONG ).show();
        }
        
        protected void onProgressUpdate(String... message) {
    		progressDialog.setMessage(message[0]);
    		progressDialog.show();
        }
    }
    
    //Upload picture to the server - will be called within the asynchronous tasks
    public void uploadPicture() {
		
			HttpClient httpclient = new DefaultHttpClient();
			HttpPost httpPost = new HttpPost(uploadURL);
			httpPost.setHeader("User-Agent", "Museum Guide Mobile App");

			try {
				MultipartEntity entity = new MultipartEntity();

				entity.addPart("type", new StringBody("file"));
				entity.addPart("data", new FileBody(new File(pathToPicture),"image/jpeg"));
				httpPost.setEntity(entity);

				HttpResponse httpResponse = httpclient.execute(httpPost);

				HttpEntity responseEntity = httpResponse.getEntity();
				if(responseEntity!=null) {
					linkToOriginal = EntityUtils.toString(responseEntity);
				}
			} catch (ClientProtocolException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}

    }
    
    //function which retrieves the finalised information from the server - will be called within the asynchronous tasks
    public void modifyPicture() {
		HttpClient httpclient = new DefaultHttpClient();
		HttpPost httpPost = new HttpPost(modifyURL);
		httpPost.setHeader("User-Agent", "SimpleCV Mobile Camera");

		try {
			List<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>(2);
	        nameValuePairs.add(new BasicNameValuePair("picture", linkToOriginal));
	        httpPost.setEntity(new UrlEncodedFormEntity(nameValuePairs));
	        
	        //the which consist of image ids and distances
			HttpResponse httpResponse = httpclient.execute(httpPost);

			responseEntity = httpResponse.getEntity();
			transformedImageURL = EntityUtils.toString(responseEntity);
			
			//reading the text file which contains the results
			try {
			    // Create a URL for the desired page
			    URL url = new URL(transformedImageURL);

			    // Read all the text returned by the server
			    BufferedReader in = new BufferedReader(new InputStreamReader(url.openStream()));
			    String rows;
			    int counter = 0;
			    while ((rows = in.readLine()) != null) {
			    	results[counter] = rows;
			    	counter++;
			    }
			    in.close();
			} catch (MalformedURLException e) {
			} catch (IOException e) {
			}
			
			//passing the result to the new activity
	    	Intent displayIntent = new Intent(getApplicationContext(),DisplayResultsActivity.class);
	    	displayIntent.putExtra("uriAsString", results);
			startActivity(displayIntent);
			
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
  }

	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		if (resultCode == RESULT_OK)
		{
			switch (requestCode){
				case TAKE_PICTURE:
					pathToPicture = pictureUri.getPath();
					break;
				case SELECT_PICTURE:
					pictureUri = data.getData();
					pathToPicture = getPathFromGallery(pictureUri);
					break;
			}
			rotation = 0;
			displayPicture();
			pictureIsSet = true;
			goButton.setClickable(true);
			counterclockwiseButton.setClickable(true);
			clockwiseButton.setClickable(true);
			linkToOriginal = null;
		}
	}

	
	 public void forcePortrait(){
		 if (pictureBitmap.getWidth() > pictureBitmap.getHeight()) {
			 rotate(90);
		 }
	 }
	 
	 public void rotate(int angle){
		 Matrix matrix = new Matrix();
		 rotation += angle;
	     matrix.preRotate(angle);
		 pictureBitmap = Bitmap.createBitmap(pictureBitmap, 0, 0, 
		                               pictureBitmap.getWidth(), pictureBitmap.getHeight(), 
		                               matrix, true);
		 
		 linkToOriginal = null;
		 refreshImage();
	 }

	 public void rotateCw(View view){
		 rotate(90);
	 }
	 
	 public void rotateCcw(View view){
		 rotate(-90);
	 }
}